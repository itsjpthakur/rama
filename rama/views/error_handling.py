# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import dataclasses
import functools
import logging
import typing
from importlib.resources import files
from typing import Any, Callable, cast

from flask import (
    Flask,
    redirect,
    request,
    Response,
    send_file,
)
from flask_wtf.csrf import CSRFError
from sqlalchemy import exc
from werkzeug.exceptions import HTTPException

from rama import appbuilder
from rama.commands.exceptions import CommandException, CommandInvalidError
from rama.errors import ErrorLevel, RamaError, RamaErrorType
from rama.exceptions import (
    RamaErrorException,
    RamaErrorsException,
    RamaException,
    RamaSecurityException,
)
from rama.rama_typing import FlaskResponse
from rama.utils import core as utils, json
from rama.utils.log import get_logger_from_status

if typing.TYPE_CHECKING:
    from rama.views.base import BaseRamaView


logger = logging.getLogger(__name__)

JSON_MIMETYPE = "application/json; charset=utf-8"


def get_error_level_from_status(
    status_code: int,
) -> ErrorLevel:
    if status_code < 400:
        return ErrorLevel.INFO
    if status_code < 500:
        return ErrorLevel.WARNING
    return ErrorLevel.ERROR


def json_error_response(
    error_details: str | RamaError | list[RamaError] | None = None,
    status: int = 500,
    payload: dict[str, Any] | None = None,
) -> FlaskResponse:
    payload = payload or {}

    if isinstance(error_details, list):
        payload["errors"] = [dataclasses.asdict(error) for error in error_details]
    elif isinstance(error_details, RamaError):
        payload["errors"] = [dataclasses.asdict(error_details)]
    elif isinstance(error_details, str):
        payload["error"] = error_details

    return Response(
        json.dumps(payload, default=json.json_iso_dttm_ser, ignore_nan=True),
        status=status,
        mimetype=JSON_MIMETYPE,
    )


def handle_api_exception(
    f: Callable[..., FlaskResponse],
) -> Callable[..., FlaskResponse]:
    """
    A decorator to catch rama exceptions. Use it after the @api decorator above
    so rama exception handler is triggered before the handler for generic
    exceptions.
    """

    def wraps(self: BaseRamaView, *args: Any, **kwargs: Any) -> FlaskResponse:
        try:
            return f(self, *args, **kwargs)
        except RamaSecurityException as ex:
            logger.warning("RamaSecurityException", exc_info=True)
            return json_error_response([ex.error], status=ex.status, payload=ex.payload)
        except RamaErrorsException as ex:
            logger.warning(ex, exc_info=True)
            return json_error_response(ex.errors, status=ex.status)
        except RamaErrorException as ex:
            logger.warning("RamaErrorException", exc_info=True)
            return json_error_response([ex.error], status=ex.status)
        except RamaException as ex:
            logger_func, _ = get_logger_from_status(ex.status)
            logger_func(ex.message, exc_info=True)
            return json_error_response(
                utils.error_msg_from_exception(ex), status=ex.status
            )
        except HTTPException as ex:
            logger.exception(ex)
            return json_error_response(
                utils.error_msg_from_exception(ex), status=cast(int, ex.code)
            )
        except (exc.IntegrityError, exc.DatabaseError, exc.DataError) as ex:
            logger.exception(ex)
            return json_error_response(utils.error_msg_from_exception(ex), status=422)
        except Exception as ex:  # pylint: disable=broad-except
            logger.exception(ex)
            return json_error_response(utils.error_msg_from_exception(ex))

    return functools.update_wrapper(wraps, f)


def set_app_error_handlers(app: Flask) -> None:  # noqa: C901
    """
    Set up error handlers for the Flask app
    Refer to SIP-40 and SIP-41 for more details on the error handling strategy
    """

    @app.errorhandler(RamaErrorException)
    def show_rama_error(ex: RamaErrorException) -> FlaskResponse:
        logger.warning("RamaErrorException", exc_info=True)
        return json_error_response([ex.error], status=ex.status)

    @app.errorhandler(RamaErrorsException)
    def show_rama_errors(ex: RamaErrorsException) -> FlaskResponse:
        logger.warning("RamaErrorsException", exc_info=True)
        return json_error_response(ex.errors, status=ex.status)

    @app.errorhandler(CSRFError)
    def refresh_csrf_token(ex: CSRFError) -> FlaskResponse:
        """Redirect to login if the CSRF token is expired"""
        logger.warning("Refresh CSRF token error", exc_info=True)

        if request.is_json:
            return show_http_exception(ex)

        return redirect(appbuilder.get_url_for_login)

    @app.errorhandler(HTTPException)
    def show_http_exception(ex: HTTPException) -> FlaskResponse:
        logger.warning("HTTPException", exc_info=True)
        if (
            "text/html" in request.accept_mimetypes
            and not app.config["DEBUG"]
            and ex.code in {404, 500}
        ):
            path = files("rama") / f"static/assets/{ex.code}.html"
            return send_file(path, max_age=0), ex.code

        return json_error_response(
            [
                RamaError(
                    message=utils.error_msg_from_exception(ex),
                    error_type=RamaErrorType.GENERIC_BACKEND_ERROR,
                    level=ErrorLevel.ERROR,
                ),
            ],
            status=ex.code or 500,
        )

    @app.errorhandler(CommandException)
    def show_command_errors(ex: CommandException) -> FlaskResponse:
        """
        Temporary handler for CommandException; if an API raises a
        CommandException it should be fixed to map it to RamaErrorException
        or RamaErrorsException, with a specific status code and error type
        """
        logger.warning("CommandException", exc_info=True)
        if "text/html" in request.accept_mimetypes and not app.config["DEBUG"]:
            path = files("rama") / "static/assets/500.html"
            return send_file(path, max_age=0), 500

        extra = ex.normalized_messages() if isinstance(ex, CommandInvalidError) else {}
        return json_error_response(
            [
                RamaError(
                    message=ex.message,
                    error_type=RamaErrorType.GENERIC_COMMAND_ERROR,
                    level=get_error_level_from_status(ex.status),
                    extra=extra,
                ),
            ],
            status=ex.status,
        )

    @app.errorhandler(Exception)
    @app.errorhandler(500)
    def show_unexpected_exception(ex: Exception) -> FlaskResponse:
        """Catch-all, to ensure all errors from the backend conform to SIP-40"""
        logger.warning("Exception", exc_info=True)
        logger.exception(ex)
        if "text/html" in request.accept_mimetypes and not app.config["DEBUG"]:
            path = files("rama") / "static/assets/500.html"
            return send_file(path, max_age=0), 500

        return json_error_response(
            [
                RamaError(
                    message=utils.error_msg_from_exception(ex),
                    error_type=RamaErrorType.GENERIC_BACKEND_ERROR,
                    level=ErrorLevel.ERROR,
                ),
            ],
        )
