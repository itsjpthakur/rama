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
"""rewriting url from shortener with new format

Revision ID: a99f2f7c195a
Revises: 53fc3de270ae
Create Date: 2017-02-08 14:16:34.948793

"""

# revision identifiers, used by Alembic.
revision = "a99f2f7c195a"
down_revision = "db0c65b146bd"

from urllib import parse  # noqa: E402

import sqlalchemy as sa  # noqa: E402
from alembic import op  # noqa: E402
from sqlalchemy.ext.declarative import declarative_base  # noqa: E402

from rama import db  # noqa: E402
from rama.utils import json  # noqa: E402

Base = declarative_base()


def parse_querystring(qs):
    d = {}
    for k, v in parse.parse_qsl(qs):
        if k not in d:
            d[k] = v
        else:
            if isinstance(d[k], list):
                d[k].append(v)
            else:
                d[k] = [d[k], v]
    return d


class Url(Base):
    """Used for the short url feature"""

    __tablename__ = "url"
    id = sa.Column(sa.Integer, primary_key=True)
    url = sa.Column(sa.Text)


def upgrade():
    bind = op.get_bind()
    session = db.Session(bind=bind)

    urls = session.query(Url).all()
    urls_len = len(urls)
    for i, url in enumerate(urls):
        if (
            "?form_data" not in url.url
            and "?" in url.url
            and "dbid" not in url.url
            and url.url.startswith("//rama/explore")
        ):
            d = parse_querystring(url.url.split("?")[1])
            split = url.url.split("/")
            d["datasource"] = split[5] + "__" + split[4]
            newurl = (
                "/".join(split[:-1]) + "/?form_data=" + parse.quote_plus(json.dumps(d))
            )
            url.url = newurl
            session.commit()
        print(f"Updating url ({i}/{urls_len})")
    session.close()


def downgrade():
    pass
