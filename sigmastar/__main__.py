from sigmastar.parse import import_module
import sys

main_module = import_module(sys.argv[1])
main_module.main()
