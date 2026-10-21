cwlVersion: v1.2
class: ExpressionTool
$namespaces:
  file: https://terradue.com/cwl/file-artifacts/v1#
requirements:
  SchemaDefRequirement:
    types:
      $import: typed-report.yaml
inputs: {}
outputs:
  report:
    type: File
    format: https://terradue.com/formats/Report
    file:contentType: typed-report.yaml#Report
    file:mediaType: application/json
expression: $(inputs)
