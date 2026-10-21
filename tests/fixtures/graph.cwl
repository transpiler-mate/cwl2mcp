# Copyright 2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cwlVersion: v1.2
$namespaces:
  s: https://schema.org/
s:name: Test tools
s:description: Offline CLI integration fixture
s:dateCreated: '2026-10-18'
s:license: https://spdx.org/licenses/Apache-2.0
s:softwareVersion: '1.0'
s:softwareHelp:
  s:url: https://example.org/help
s:publisher:
  s:name: Example
s:author:
  s:givenName: Example
  s:familyName: Author
  s:email: author@example.org
  s:affiliation:
    s:name: Example
$graph:
  - id: main
    class: Workflow
    inputs: {region: string}
    outputs: {}
    steps: {}
  - id: echo
    class: CommandLineTool
    baseCommand: echo
    inputs: {region: string}
    outputs: {}
  - id: expression
    class: ExpressionTool
    inputs: {region: string}
    outputs: {region: string}
    expression: $(inputs)
