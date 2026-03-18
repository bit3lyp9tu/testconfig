
# TestConfig

1. installation via pip (pip install mtt). du kannst aber auch das alles vorbereiten, kann dir dann zeigen wie und dann "pip install git+https://github.com/..." nehmen
2. ich würde anfangen mit einer config-file die das projekt selbst testet. nehme yaml weil das gut und einfach lesbar ist. parse die yaml file in nem python script. die sollte folgendes enthalten:
- sprache
- test-typen
- erwartete tests
- abhängigkeiten der tests

```yaml
python:
    mtt.py:
        - venv: requirements.txt # Temporäre venv sollte daraus automatisch erstellt und geladen werden; schlägt die Installation der venv fehl -> test fails
        - only_run_when_changed: [mtt.py, mathstuff.py] # Nur ausführen, wenn eine hiervon geändert worden ist; optional, wenn nicht gesetzt immer ausführen
        - tests:
            - add: # Funktionsname
                - input: [1, 2, 3]
                - output: 6
            - test_komplex:
                - input: 123
                - output: 456
                - expected_output: "success" # stdout muss "success" sein
                - needs: [add] # Nur ausführen, wenn der add tests geklappt hat, auf dieser Ebene bezieht es sich auf die anderen Tests in der mtt.py
php:
    functions.php:
        - only_run_when_changed: functions.php # Optional, nur wenn diese Datei geändert worden ist ausführen (oder immer wenn andere Bedingungen wie needs gegeben)
        - needs: [mtt.py] # Optional, wenn nicht immer ausführen; sonst nur wenn die gesamte test-gruppe mtt.py durch ist
        - tests:
            - multiply: # Funktionsname in PHP-Datei
                - input: > # Multi Line string, one line = one input parameter set
                    [1, 2]
                    [3, 4]
                    [10, 20, 30]
                -output: >
                    2
                    12
                    6000
            - divide:
                - needs: multiply # only run when multiply is done
                    - csv: path/to/results/of/multiply.csv # CSV mit x0,x1,x2,..., y0[,y1,y2,...] und ergebnissen die reingehen/rauskommen sollen; gern auch andere formate wie multiline yaml oder sowas implementieren
            - greet:
                - wanted_stdout: "hello" # führt die fkt aus und schaut, ob im stdout (print) da "hello" steht, wenn nein, test gefailt
                - needs: divide
            - divide_by_zero: # führt die fkt divide_by_zero aus die das programm zum crashen bringt
                - exit_code: 1 # Programm muss da crashen mit exit-code 1
```

tests die keine abhängigkeiten voneinander haben kann man parallel ausführen. ob ne datei geändert worden ist kannste mit git log rausfinden. kein git log oder keine history -> wird immer ausgeführt (aber mit warning)

sprach-erweiterungen:

jede sprache (erste ebene der yaml) sollte ausschließlich per [sprache].yaml, zB python.yaml oder php.yaml, definiert sein. die beinhalten sowas wie:

python3.yaml:
```yaml
- unit-test:
    - steps:
        - single_test_code: >
if(%module%.%function%(%parameter) != %wanted%):
    sys.exit(1)

        - code: >
import %module%
import sys

%single_test_code%

        - run:
            - command: python3 %file%
            - exit_code: 0

    - exit_code:
        - command: "python3 %filename%"
        - return: %exit_code%

```

hier sind 2 typen definiert. typ 1 lädt die python datei als modul. dafür darf sie keine unerwarteten side-effects haben (bedingungen an den programmierer damit er das nutzen kann, ist auch aber clean code).

der soll dann aus nem test oder mehreren tests code bauen indem er die datei als modul lädt, und die fkt ausführt. aus

```
if(%module%.%function%(%parameter) != %wanted%):
```

wird dann zB:

```
if(mtt.add(1, 1) != 2):
```

und der exited mit 1 wenn das failt. das ganze wird dann in ne temp file geschrieben und mit python3 /pfad/zur/temp/datei.py ausgeführt und der exit-code gecheckt, und stdout usw. für tests von stdout usw. mitgeloggt (das kann man zentral machen, egal welche sprache man da nutzt)

das gleiche prinzip kann man dann für php anwenden indem man ne php.yaml schreibt, die halt php testing code generiert, in ne temp datei schreibt und mit php /pfad/zur/temp/datei.php ausführt.

so wär ideal mEn
wenn du eh strings für massen-tests benutzt kannste auch statt da input und output zu haben sowas haben:
```
- concat: >
    1,2,3,4 -> 1234
    4,3,2,1 -> 4321
```

wäre cool wenn man auch neue flags hinzufügen könnte, sowas wie check_exit_code_only: bash irgendwas.sh, was dann stdout usw alles ignoriert und nur den exit-code zurückgibt, und die config was da gemacht wrird iwie in check_exit_code_only.yaml oder so läge. damit wär man komplett flexibel und erweiterbar. genauso wie man da ne playwright.yaml haben könnte die n browser startet und js ausführt und den return code zurückgibt oder sowas. paar defaults (python, php, playwright usw.) kannste mitliefern per default, wer mehr will muss sie selbst schreiben
und du könntest direkt das programm selbst damit testen, und den poster generator, damit du direkt n bsp hast wo du siehst wie mans noch verbessern kann und auch das andere projekt einbeziehst

```python
if test_module.multiply(0.5,10,-1) != -5.0:
	print('[FAIL] tests/code/test.py#multiply(0.5,10,-1) != -5.0')
	sys.exit(1)

if test_module.addAll(1,2,3,4,5,6) != 21:
	print('[FAIL] tests/code/test.py#addAll(1,2,3,4,5,6) != 21')
	sys.exit(1)

spec = importlib.util.spec_from_file_location("test_module2", ROOT / "tests/configs/config5.py")
test_module2 = importlib.util.module_from_spec(spec) # type: ignore
spec.loader.exec_module(test_module2) # type: ignore

if test_module2.complex_test() != :
	print('[FAIL] tests/code/test.py#complex_test() != ')
	sys.exit(1)
```
