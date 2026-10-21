cwlVersion: v1.2
class: ExpressionTool
id: types
requirements:
  SchemaDefRequirement:
    types:
      - name: Node
        type: record
        fields:
          - name: value
            type: string
          - name: children
            type:
              type: array
              items: Node
inputs:
  flag: {type: boolean, default: false}
  count: {type: int, default: 0}
  text: {type: string, default: ''}
  empty: {type: 'string[]', default: []}
  optional: ['null', string]
  nullOnly: 'null'
  integer: long
  number: double
  union: [int, string]
  nested:
    label: Nested array
    doc: [First paragraph., Second paragraph.]
    type:
      type: array
      items: {type: array, items: float}
  record:
    type:
      name: Envelope
      type: record
      fields:
        - name: mode
          type: {type: enum, name: Mode, symbols: [fast, slow]}
        - name: detail
          type:
            type: record
            name: Detail
            fields:
              - {name: enabled, type: boolean}
  tree: types/Node
  unrelated:
    type:
      name: URI
      type: record
      fields:
        - {name: value, type: string}
outputs:
  result: string
expression: '$({result: "ok"})'
