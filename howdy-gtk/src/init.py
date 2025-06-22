# Opens auth ui if requested, otherwise starts normal ui
import sys

if "--start-auth-ui" in sys.argv:
	import authsticky
else:
	import window
