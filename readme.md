# about
* Takes as input the raw xlsx files dumps from dbase
* treats stuff like dates, missing data, nulls
* renders them into cleaned .csv that we can build fixtures from in django using the django model parser

# usage

## general syntax & notes on usage
>$ python main.py --configs [config filepath] --mode [one of mode defined in config file]

* Both are arguments are optional
  * configs defaults to `./configs.yaml` from rootdir
  * mode defaults to `default`

NOTE: the default values are always set, regardless of the mode selected. What the other modes do is that they
override any such values with whatever is put there. No need to fully re-defined all attribute if using
a non-default mode.

## basic usage
>$ python main.py

## merging files
>$ python main.py --mode merge

* specify `xlsx_root`, `inputs_folder`, `outputs_folder` as needed in configs.yaml 

