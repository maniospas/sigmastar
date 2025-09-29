from sigmastar.parse import import_module
import sys

try: 
    main_module = import_module(sys.argv[1])
    main_module.main()
except Exception as e:
    print(str(e))

