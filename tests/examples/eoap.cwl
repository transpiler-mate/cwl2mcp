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

$namespaces:
  agent: https://eoap.github.io/cwl-mcp-extension#
  s: https://schema.org/
s:name: Inspect source
s:description: Inspect a spatial source without changing its records.
s:dateCreated: "2026-10-18"
s:license:
  "@type": s:CreativeWork
  s:identifier: CC-BY-4.0
  s:name: "Creative Commons Attribution 4.0 International"
  s:url: https://spdx.org/licenses/CC-BY-4.0.html
s:keywords:
  - CWL
  - Workflow
  - "Earth Observation"
s:operatingSystem:
  - Linux
s:softwareRequirements:
  - https://cwltool.readthedocs.io/en/latest/
  - https://www.python.org/
s:softwareVersion: 3.0.0
s:softwareHelp:
  - "@type": s:CreativeWork
    s:name: "User Manual"
    s:url: https://meoga-shiny-workflow.readthedocs.io/en/latest/
  - "@type": s:CreativeWork
    s:name: "Admin Manual"
    s:url: https://meoga.io/meoga/shiny-workflow/admin
s:publisher:
  "@type": s:Organization
  s:name: "Make Earth Observation Great Again"
  s:email: "info@meoga.com"
  s:identifier: https://ror.org/9999cx000
s:author:
  - "@type": s:Role
    s:roleName: Conceptualization
    s:startDate: "2025-01-01"
    s:additionalType: https://credit.niso.org/contributor-roles/conceptualization/
    s:author:
      "@type": s:Person
      s:givenName: Lex
      s:familyName: Luthor
      s:email: "lex.luthor@luthorcorp.com"
      s:identifier: https://orcid.org/0000-9999-0000-9999
      s:affiliation:
        "@type": s:Organization
        s:name: "Luthor Corp"
        s:identifier: https://ror.org/0000cx000


cwlVersion: v1.2
class: ExpressionTool
id: main
label: Inspect a spatial source
doc: Return a source URI, timestamp and GeoJSON point without changing their records.
requirements:
  SchemaDefRequirement:
    types:
      - $import: https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml
      - $import: https://raw.githubusercontent.com/eoap/schemas/main/geojson.yaml
hints:
  agent:Tool:
    name: inspect_source
    title: Inspect Source
    useWhen: the user needs to inspect a spatial source.
    doNotUseWhen: the user needs data modification.
    aliases: [inspect a spatial source]
    annotations:
      readOnlyHint: true
      destructiveHint: false
      idempotentHint: true
      openWorldHint: false
inputs:
  source:
    type: https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URI
    label: Source URI
  timestamp:
    type: https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#DateTime
  point:
    type: https://raw.githubusercontent.com/eoap/schemas/main/geojson.yaml#Point
outputs:
  source_result: https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URI
  timestamp_result: https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#DateTime
  point_result: https://raw.githubusercontent.com/eoap/schemas/main/geojson.yaml#Point
expression: '$({source_result: inputs.source, timestamp_result: inputs.timestamp, point_result: inputs.point})'
