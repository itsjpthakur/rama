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
from wtforms.form import Form

from rama.forms import CommaSeparatedListField, filter_not_empty_values
from tests.integration_tests.base_tests import RamaTestCase


class TestForm(RamaTestCase):
    def test_comma_separated_list_field(self):
        field = CommaSeparatedListField().bind(Form(), "foo")
        field.process_formdata([""])
        assert field.data == [""]

        field.process_formdata(["a,comma,separated,list"])
        assert field.data == ["a", "comma", "separated", "list"]

    def test_filter_not_empty_values(self):
        assert filter_not_empty_values(None) is None
        assert filter_not_empty_values([]) is None
        assert filter_not_empty_values([""]) is None
        assert filter_not_empty_values(["hi"]) == ["hi"]
