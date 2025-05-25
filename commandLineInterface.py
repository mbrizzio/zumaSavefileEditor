import subprocess
from enum import Enum
from pathlib import Path

# Parses user argumenst for commands that may or may not take several arguments
def parseUserInputs(response: str) -> dict[str, str]:
  arguments = {}
  
  response = response.strip()
  for pair in response.split(","):
    pair = [side.strip() for side in pair.split("=")]
    
    arguments[pair[0]] = pair[1]
  
  return arguments

class Editor:
  # Reads in all the attributes from config.txt
  def __init__(self):
    
    # TODO: Make it so a config.txt file gets automatically generated if the user doesn't have one
    with open("config.txt", "r") as config:
      lines = [line.strip() for line in config.readlines()]
      
      # Location of adv{slot}.sav; absolute path
      self.saveLocation = Path(lines[0].split(":::")[1])                  
      
      # Location of Zuma.exe; absolute path
      self.gameLocation = Path(lines[1].split(":::")[1])  
      
      # How many points the savefile should have
      self.points = int(lines[2].split(":::")[1]).to_bytes(3, byteorder="little")
      
      # How the program should behave after a level is selected               
      self.behavior = lines[3].split(":::")[1] 
      
      # Which slot you are using
      self.slot = int(lines[4].split(":::")[1])  
      
      # Whether or not you want to see the explanatory message at the beginning         
      self.help = bool(int(lines[5].split(":::")[1]))      
  
  # Use this to update any value from the config file; only does so internally
  def changeConfigParameters(
  self,
  saveLocation = None,
  gameLocation = None,
  points =       None,
  behavior =     None,
  slot =         None,
  help =         None):
    
    if (saveLocation != None):
      self.saveLocation = Path(saveLocation)
    
    if (gameLocation != None):
      self.gameLocation = Path(gameLocation)
    
    if (points != None 
    and 0 <= int(points) and int(points) <= self.MAXPOINTS):
      self.points = int(points).to_bytes(3, byteorder="little")
    
    if (behavior != None
    and behavior.upper() in self.BEHAVIORS):
      self.behavior = behavior.upper()
    
    if (slot != None
    and int(slot) >= 0 and int(slot) <= 9):
      self.slot = int(slot)
    
    if (help != None
    and (int(help) == 0 or int(help) == 1)):
      self.help = bool(int(help))
    
    self.saveConfigParameters()
  
  # Print your current settings    
  def printConfigParameters(self):
    configuration = fr"""
    saveLocation: {self.saveLocation}
    gameLocation: {self.gameLocation}
    points: {int.from_bytes(self.points, byteorder='little')}
    behavior: {self.behavior}
    slot: {self.slot}
    help: {self.help}
    """
    
    print(configuration)
  
  # Use this to transfer your config values from the object to the config.txt file
  def saveConfigParameters(self):
    configuration = fr"""
  SAVELOCATION:::{self.saveLocation}
  GAMELOCATION:::{self.gameLocation}
  POINTS:::{int.from_bytes(self.points, byteorder='little')}
  DEFAULTBEHAVIOR:::{self.behavior}
  SAVEFILESLOT:::{self.slot}
  HELPMESSAGE:::{int(self.help)}
  """.strip()
  
    with open("config.txt", "w") as file:
      file.write(configuration)
  

  
  # Use this to change which level you want to play
  # Argument expects the same format the game uses: [world]-[level]
  def selectLevel(self, location: str):
    world = int(location.split("-")[0])
    level = int(location.split("-")[1])
    
    # TODO: Figure out a better failsafe than this
    if level not in self.LEVELS[world][0]:
      print("invalid level for the world")
      return
    
    byte = level + self.LEVELS[world][1] - 1
    
    with open("adv1.sav", "rb") as file:
      self.savefile = bytearray(file.read())
      self.savefile[self.LEVELBYTELOCATION] = byte
      
    self.enactBehavior()
  
  
  # Use this to overwrite your savefile in the SAVELOCATION based on your saveslot
  # WARNING: this deletes your current game for that user! It has no effects on high scores or anything though
  # DO NOT USE OUTSIDE enactBehavior()!
  def saveEditedSavefile(self):
    with open("edited.sav", "wb") as file:
      file.write(self.savefile)
    
    command = fr'copy .\edited.sav "{self.saveLocation}\adv{self.slot}.sav"'
    subprocess.run(command, shell=True)
    
    
    # Very weird bug where 12-6 in particular just does not want to work, idk why
    # when I check teh savefile of a 12-6, it has hex 49, which is the same as 12-7. 
    # But 12-7 works just fine? idk
  
  
  # Use this to run Zuma.exe
  def runGame(self):
    subprocess.run(fr"{self.gameLocation}", shell=True)
  
  
  # Use this to exit the program
  def closeProgram(self):
    # Not necessary but it ensures your changes are saved in case something happens
    self.saveConfigParameters()
    
    exit(0)
  
  # Do what the user wants based on their settings
  def enactBehavior(self):
    if self.behavior == "SAVE":
      self.saveEditedSavefile()
      
    elif self.behavior == "LAUNCH":
      self.saveEditedSavefile()
      self.runGame()
    
    elif self.behavior == "CLOSE":
      self.saveEditedSavefile()
      self.runGame()
      self.closeProgram()
      
    else:
      print("Catastrophic error with config file")
      print("Resetting config file back to defaults")
      # TODO: Reset it back to defaults once changeConfigParameters is implemented
      
      
  
  # Getter function to tell you whether or not you have get as a bool
  def getHelp(self) -> bool:
    return self.help
  
  ### Universal variables to define consistent rules around which levels are valid
  # Levels has a set of valid levels per world; catches invalid levels (like 1-7)
  # it also has the offset you need. In the file, 6 = 2-1 for instance, so the 
  # offset for world 2 is 5
  # Levels are -1; 00 actually corresponds to 1-2, not 1-1
  LEVELS = {
    1: ((1, 2, 3, 4, 5), 0),
    2: ((1, 2, 3, 4, 5), 5),
    3: ((1, 2, 3, 4, 5), 10),
    4: ((1, 2, 3, 4, 5, 6), 14),
    5: ((1, 2, 3, 4, 5, 6), 20),
    6: ((1, 2, 3, 4, 5, 6), 26),
    7: ((1, 2, 3, 4, 5, 6, 7), 32),
    8: ((1, 2, 3, 4, 5, 6, 7), 39),
    9: ((1, 2, 3, 4, 5, 6, 7), 46),
    10: ((1, 2, 3, 4, 5, 6, 7), 53),
    11: ((1, 2, 3, 4, 5, 6, 7), 60),
    12: ((1, 2, 3, 4, 5, 6, 7), 67),
    13: ((1, 1), 74)
  }
  
  # Behaviors is the list of strings that are valid for the DEFAULTBEHAVIOR section, which defines what to do once you change level
  # SAVE: overwrite your savefile with the edited one generated by the script
  # LAUNCH: SAVE + the game gets automatically launched
  # CLOSE: LAUNCH + script automatically closes itself
  BEHAVIORS = ("SAVE", "LAUNCH", "CLOSE")
  
  # This is the exact location where the byte that controls the level you are on is set
  LEVELBYTELOCATION = 16*2+4
  
  # This is the maximum points you can have in the savefile
  MAXPOINTS = 0xFFFFFF

class State(Enum):
  START = 0
  LEVEL = 1
  CONFIG = 2
  STATE = 3
  KILL = 10

configurator = Editor()
state = State(0)
response = ""
helpMessage = fr"""
List of commands:
level (l): 
  Lets you select which level you want to play
  Takes in 1 argument in the form [world]-[level]
  Example: level 13-1

config (c):
  Lets you change the parameters of the config.txt file, which contains the following:
    saveLocation: absolute filepath of the location of your savefile
    Example: saveLocation="C:\ProgramData\Steam\Zuma\userdata"
    gameLocation: absolute filepath of the location of Zuma.exe
    Example: gameLocation="C:\Program Files (x86)\Steam\steamapps\common\Zuma Deluxe\Zuma.exe"
    points: how many points you want your savefile to have. 0 <= points <= 16777215
    Example: points=100000
    behavior: how the program should behave after you select a level
      SAVE: overwrite your save to have the new level
      LAUNCH: overwrite the save and launch the game
      CLOSE: overwrite the save, launch the game, and close this script
    Example: behavior=LAUNCH
    slot: which slot you want to save to, determined by teh order of your profiles in the game
    Example: slot=1
    help: whether or not you want to see this message. Has to be 1 or 0
    Example: help=1
  You can edit any number of these when calling this function
  Arguments are separated by commas
  Example: config saveLocation=D:\, points=123456
  
state (s):
  See your current configuration settings
  example: state

end (e): 
  closes the program

"""

# State machine that controls the program
while True:
  # Default state. This is the state you get when launching the program
  if state == State.START:
    
    if configurator.getHelp():
      print(helpMessage)
    
    response = input("Pass your command:\n")
    command = response.split(" ")[0]
    if command[0] == "l":
      if len(response.split(" ")) == 2:
        state = State.LEVEL
      else:
        print("Incorrect number of arguments")
    
    elif command[0] == "e":
      state = State.KILL
      
    elif command[0] == "c":
      state = State.CONFIG
    
    elif command[0] == "s":
      state = State.STATE
    
    else:
      print("command not found")
   
    
  # State where you change level
  # Get here if you called 
  if state == State.LEVEL:
    level = response.split(" ")[1]
    
    configurator.selectLevel(level)
    
    state = State.START
  
  # Configure the file
  if state == State.CONFIG:
    unparsedArguments = response.split(" ", 1)[1]
    kwargs = parseUserInputs(unparsedArguments)
    
    configurator.changeConfigParameters(**kwargs)
    
    state = State.START
  
  # Print your current settings
  if state == State.STATE:
    configurator.printConfigParameters()
    
    state = State.START
    
    
  # End the application
  if state == State.KILL:
    configurator.closeProgram()