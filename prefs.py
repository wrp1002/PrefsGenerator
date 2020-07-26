
import inspect

# ======================== Customization ========================

companyName = "companyname"
defaultReloadPrefsFunction = "ReloadPrefs"
outputFile = "output.txt"


# ======================== Other variables ========================

tweakName = "tweakname"
packageName = "com." + companyName + "." + tweakName
prefsTitle = "Title"

header = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>items</key>
	<array>
"""

footer = """
	</array>

	<key>title</key>
	<string>PrefsTitle</string>
</dict>
</plist>
"""


finalFile = header


# ======================== Misc Functions ========================

def GetDataType(val):
	if type(val) is list:
		return "array"

	val = str(val)

	if not val.isdigit() and val.replace('.','',1).isdigit():
		return "real"
	elif val.isdigit():
		return "integer"
	elif val.lower() == "true" or val.lower() == "false":
		return "bool"
	else:
		return "string"


def GetInput(prompt, defaultValue, acceptableInputs = []):
	response = str(input(prompt + " [" + (str(defaultValue) if str(defaultValue) else "Enter to skip") + "]: "))

	if acceptableInputs and response and response not in acceptableInputs:
		print("Invalid input")
		response = GetInput(prompt, defaultValue, acceptableInputs)

	return response if response else defaultValue

def GetInputWithBounds(prompt, min, max):
	val = min - 1
	while val < min or val > max:
		val = input(prompt)
		if not val.isdigit():
			val = min - 1
		val = int(val)

	return val


def BuildDict(cellType, tags):
	global finalFile

	newDict =  "		<dict>\n"
	newDict += "			<key>cell</key>\n"
	newDict += "			<string>" + cellType + "</string>\n"


	for key in tags.keys():
		if not tags[key]: 
			continue

		val = tags[key]
		dataType = GetDataType(val)

		newDict += "			<key>" + key + "</key>\n"
		if dataType == "bool":
			val = str(val)
			newDict += "			<" + val.lower() + "/>\n"
		elif dataType == "array":
			newDict += "			<array>\n"
			
			for i in tags[key]:
				val = str(i)
				dataType = GetDataType(val)
				newDict += "				<" + dataType + ">" + val + "</" + dataType + ">\n"

			newDict += "			</array>\n"
		else:
			val = str(val)
			newDict += "			<" + dataType + ">" + val + "</" + dataType + ">\n"
	
	newDict += "		</dict>\n\n"

	finalFile += newDict
	


# ======================== Cell Functions ========================

def PSGroupCell():
	tags = {}
	tags["label"] = GetInput("Group Cell Title", "")
	tags["footerText"] = GetInput("Group Cell Footer", "")
	BuildDict(inspect.currentframe().f_code.co_name, tags)

def PSSwitchCell():
	tags = {}
	tags["label"] = GetInput("Label", "Enabled")
	tags["key"] = GetInput("Key", "k" + tags["label"])
	tags["default"] = GetInput("Default", "true", ["true", "false"])
	tags["defaults"] = GetInput("Defaults", packageName)
	#tags["alternateColors"] = GetInput("Alternative colors", "false")	# only works on iOS<7  :(
	tags["PostNotification"] = GetInput("PostNotification", packageName + "/" + defaultReloadPrefsFunction)

	BuildDict(inspect.currentframe().f_code.co_name, tags)

def PSSliderCell():
	tags = {}

	tags["key"] = GetInput("Key", "kSlider")
	tags["min"] = GetInput("Minimum", 0)
	tags["max"] = GetInput("Maximum", 10)
	tags["showValue"] = GetInput("Show Value", "true", ["true", "false"])
	tags["isSegmented"] = GetInput("Is Segmented", "false", ["true", "false"])
	if tags["isSegmented"] == "true":
		tags["segmentCount"] = GetInput("SegmentCount", 1)
	tags["default"] = GetInput("Default", tags["min"])
	tags["defaults"] = GetInput("Defaults", packageName)
	tags["PostNotification"] = GetInput("PostNotification", packageName + "/" + defaultReloadPrefsFunction)
	BuildDict(inspect.currentframe().f_code.co_name, tags)

def PSSegmentCell():
	tags = {}

	tags["key"] = GetInput("Key", "kSlider")

	amount = GetInput("Amount of titles", 2, [2, 3, 4, 5, 6, 7, 8, 9, 10])
	titles = []
	values = []
	for i in range(amount):
		titles.append(GetInput("Enter title " + str(i), "Title" + str(i)))
		values.append(GetInput("Value", i))
	
	tags["validTitles"] = titles
	tags["validValues"] = values

	tags["default"] = GetInput("Default", 0)
	tags["defaults"] = GetInput("Defaults", packageName)
	tags["PostNotification"] = GetInput("PostNotification", packageName + "/" + defaultReloadPrefsFunction)
	BuildDict(inspect.currentframe().f_code.co_name, tags)


cellFunctions = [PSGroupCell, PSSwitchCell, PSSliderCell, PSSegmentCell]


# ======================== Main ========================

if __name__ == "__main__":
	print("Values inside [] are defaults. Press enter to accept them\n")
	tweakName = GetInput("Enter tweak name", tweakName)
	packageName = GetInput("Enter package name", "com." + companyName + "." + tweakName)

	while True:
		print()

		for i in range(len(cellFunctions)):
			print(str(i+1) + ". " + cellFunctions[i].__name__)
		print(str(len(cellFunctions)+1) + ". Done")
		
		index = GetInputWithBounds(">", 1, len(cellFunctions) + 1)

		if index < len(cellFunctions) + 1:
			cellFunctions[index-1]()
		else:
			break
	
	title = GetInput("Title", tweakName)

	finalFile += footer.replace("PrefsTitle", title)

	print()
	print(finalFile)
	with open(outputFile, 'w') as file:
		file.write(finalFile)
		
	print()
	print("Wrote to", outputFile)
