
# Config
## General Configuration

Example:
```yaml
<Test-Unit>:
    <path-of-tested-file>:
        only_run_when_changed:
            - whitelist: []
            - blacklist: []
        test:
            - <name-of-function-to-test>:
                - <parameters> -> <expected-result>
                - <other-parameters> -> <other-expected-result>
            - <an-other-function>:
                csv_path: '<path-to-csv-file>'

```

- `<Test-Unit>` must have an associated configuration file with the path `lang/<Test-Unit>.yaml`

currently unused:
```yaml
only_run_when_changed:
    - whitelist: []
    - blacklist: []
```

- to test a function a the exact function name as a child of `test` and add additional children with the `<parameters> -> <expected-result>` or add `csv_path: <path-to-csv-file>`

- The format of the csv file should be:
```csv
function;x_n;y_n
multiply;[7,8,9];[504]
multiply;[10,11,12];[1320]
multiply;[-1,10,1];[-10]
multiply;[0.5,10,-1];[-5.0]
```

## Test-Unit specific Configuration

Example configuration for `python.yaml`

```yaml
config:
    variable_infix_char: "%"
    variables:
        import_module: "%your-module%"
        function_name: "%your-function_name%"
        parameters: "%your-parameters%"
        expected_result: "%your-expected_result%"
        calculated_result: "%your-calculated_result%"
```

TODO: `unit-test`

```yaml
hooks:
    <name-of-hook>:
        name: "<name-of-hook>"
        attributes:
            - <env-var1>
            - <a-path>
        commands:
            - <command1>
            - <command2>
        activation_time: "<before-or-after>"
        description: "<description-of-hook>"
```

- `attributes` contains a list of environmental variables that should be set before running the hook. They can be defined in the general configuration file in chronological order.
- `commands` lists which commands should be executed when the hook is called.
- `activation_time` expresses when the hook should be activated relative to the place in general config file. The possible values are `before` and `after`.

## TODO

- Define a clear list of hooks, warn if a hook is defined that isn't in that list
- Trennen zwischen Attributes (Sachen die intern sein sollen) und Environment (env vars)
- Hooks: wie führt man sie aus? Ist es immer bash?
-> command: "..." in der Hook-definition erlauben so dass man eigene Kommandos definieren kann

```python3
language = yaml.get()

if language.get("hook").get("setup"):
    run_setup_hook()

for each test:
    if language.get("hook").get("single_test_setup"):
        run_single_test_setup_hook()

    subprocess.run("python3 dein/test.script")

    if language.get("hook").get("single_test_shutdown"):
        run_single_test_shutdown_hook()

if language.get("hook").get("shutdown"):
    run_shutdown_hook()
```

-> Resultat: du hast ne fest definerte Liste von Stellen im Code wo Hooks ausgeführt werden; jeder davon hat einen Namen
