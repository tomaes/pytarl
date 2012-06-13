"""

  pytarl, v0.7a2
  ............................................................................  
  a small console/terminal text adventure-like rougelike dungeon crawler game
  written in Python 2.6.x
  by Thomas Gruetzmacher (tomaes.32x.de)  
  ............................................................................
  Licence:     this source code is licenced under Creative Commons (CC-BY) 
               http://creativecommons.org/licenses/by/3.0/deed.en

"""

import sys
import random as rand

# default declarations
APP_NAME    = "pytarl"
APP_VERSION = "0.7a2"

class DUNGEON:
    DIST_EXIT   =    8
    SIZE_MIN    =   10
    SIZE_DEF    =  100
    SIZE_MAX    = 1000
    POS_START   = (50,50) # (0,0)
    DIST_TEMPLE = SIZE_DEF / 10
    # object distribution, obj count per 100 dungeon tiles
    DISTRI_PERCENT = { "CHESTS"   :  8,  \
                       "ADVE"     :  4,  \
                       "WIZARDS"  :  2,  \
                       "MONSTERS" : 10,  \
                       "TRAPS"    :  8,  \
                       "FUNGI"    :  3,  \
                       "CASINOS"  :  2 }
    TRAP_PENALTY   = 10
    FUNGI_ADDLOAD  = 10

class TEMPLE:
    RUNES_WANTED =   7
    REWARD_MIN   = 500
    REWARD_MAX   = 800

class SCORE:
    RUNES       =  10
    PICKAXE     =  10
    IDOL        = 100
    FOOD        =   1
    TURNS       =  -1
    POTION_INV  =  25
    TEMPLE_SEEN =  50
    
class Player:
    x, y        = DUNGEON.POS_START
    turns       = 0
    runes       = 0
    fungi       = 0
    fungi_load  = 0 # how much that funky poison is still in your system?   
    gold        = DUNGEON.SIZE_DEF / 2
    food        = DUNGEON.SIZE_DEF / 2 + 25
    compass     = True
    pickaxe     = False
    potion_inv  = False
    temple_seen = False
    idol        = False
    pickaxe_use = 0
    PICKAXE_DURABILITY = 10
    FUNGI_MAX          = 20

class Dungeon:
    dungeon  = [ (Player.x, Player.y) ]    
    temple   = (0,0)
    exit     = (0,0)
    objects  = []  # all ocupied dungeon positons
    visited  = [] 
    chests,   adve,     \
    wizards,  monsters, \
    traps,    fungi,    \
    casinos   = [], [], [], [], [], [], []

KEY_NORTH  = 'n'; KEY_SOUTH  = 's'
KEY_EAST   = 'e'; KEY_WEST   = 'w'
KEY_NOMOVE = '.'; KEY_FUNGI  = 'f'
KEY_HELP   = '?'; KEY_INFO   = 'i'

key = KEY_NOMOVE;

KEYS_MOVE = { KEY_NORTH: ( 0,-1 ), \
              KEY_SOUTH: ( 0, 1 ), \
              KEY_EAST:  ( 1, 0 ), \
              KEY_WEST:  (-1, 0 ), \
              KEY_NOMOVE:( 0, 0 ) }
              
KEYS_MISC = [ KEY_HELP, KEY_INFO ]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  help and info screens
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def show_help():

    print "\nHere Be Dragons... and some info too:\n"
    print "* Enter '" + KEY_NORTH + "','" + KEY_SOUTH + "','" + KEY_EAST + "','" + KEY_WEST + "' to go north/south/east/west or"
    print "  enter '" + KEY_NOMOVE + "' to let a turn pass to check your sourroundings instead."
    print "* Enter '" + KEY_INFO + "' to see the status page."
    print "* The compass tells you how far off the exit is (x/y),"
    print "  however, it does not give you directions."
    print "* Collect as much gold as you can."
    print "* Find the exit of this Dungeon."
    print "* Don't run out of food! Every turn, you consume one of your food rations."
    print "* There are other travelers in this Dungeon!"
    print "* Beware of vicious monsters. They have dice!"
    print "* Also, beware of traps. Your detection device will tell how many traps"
    print "  are nearby in all 4 directions (e.g. 0..3)"
    print "* Find the hidden temple!"
    print "* Weird fungi grow all over the dungeon. Don't eat those? Or maybe you should?"
    print "* You can create differently sized dungeons by using a command line parameter"
    print "  (e.g. dungeon.py", DUNGEON.SIZE_MAX, "will create a huge dungeon for you).\n"
    print "That's all... for now. Good Luck!\n"

def show_info( _Player, _Dungeon ):

    print "\nSTATUS:"
    print " * Position        :", str( (_Player.x, _Player.y) ).ljust(10),
    print " * Runes collected :", _Player.runes 
    print " * Golden coins    :", str(_Player.gold).ljust(10),
    print " * Turns so far    :", _Player.turns
    print " * Food rations    :", str(_Player.food).ljust(10),
    print " * Fungi collected :", str(_Player.fungi)
    print " * Temple visited  :",
    if _Player.temple_seen:
        print "Yes"
    else:
        print "No"

    print "\nITEMS:"
    if _Player.compass:
        print " + Compass (to show you the distance to the exit)"
    if _Player.pickaxe:
        print " + Pickaxe (to digg through walls)"
    if _Player.potion_inv:
        print " + Potion of invisibility (to sneak behind monsters)"
    if _Player.idol:
        print " + GOLDEN IDOL (for fame and profit!)"

    met_monsters = list( set( _Dungeon.visited ).intersection( _Dungeon.monsters ) )
    met_wizards  = list( set( _Dungeon.visited ).intersection( _Dungeon.wizards  ) )
    met_adve     = list( set( _Dungeon.visited ).intersection( _Dungeon.adve     ) )
    seen_casinos = list( set( _Dungeon.visited ).intersection( _Dungeon.casinos  ) )
        
    print "\nLOG:"
        
    if met_monsters + met_wizards + met_adve + seen_casinos == [] and \
        _Dungeon.exit not in _Dungeon.visited:
        print " # Nothing so far."
    else:
        if met_monsters:
            print " # Monster(s) at:",    str( met_monsters )[1:-1]
        if met_wizards:
            print " # Wizard(s) at:",     str( met_wizards  )[1:-1]
        if met_adve:    
            print " # Adventurer(s) at:", str( met_adve     )[1:-1]
        if seen_casinos:    
            print " # Casino(s) at:",     str( seen_casinos )[1:-1]
        if _Dungeon.exit in _Dungeon.visited:
            print " # Exit at: ", _Dungeon.exit
    print 
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  create a simple random dungeon, with radomly spread gold etc.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def create_dungeon( _size, _Dungeon, _DUNGEON ):

    x, y = _DUNGEON.POS_START

    # generate maze
    while len( _Dungeon.dungeon ) < _size:
        xd = rand.randint( -1, 1 )
        if xd is 0:
            yd = rand.randint( -1, 1 )
        else:
            yd = 0
        x += xd; y += yd
        if (x,y) not in _Dungeon.dungeon:
            _Dungeon.dungeon.append( (x,y) )
                        
    # the exit should not be near the extrance
    for i in range( len(_Dungeon.dungeon)-1, -1 ):
        if abs(_Dungeon.dungeon[i][0]) + abs(_Dungeon.dungeon[i][1]) >= _DUNGEON.DIST_EXIT:
            _Dungeon.exit = _Dungeon.dungeon[i]
            
    # nothing far enough found? pity, last tile it is
    if _Dungeon.exit == (0,0):
        _Dungeon.exit = _Dungeon.dungeon[-1]
    
    # setup temple outside the maze
    rx   = ry = 0
    dist = _DUNGEON.DIST_TEMPLE
    while (rx, ry) in _Dungeon.dungeon:
        rx, ry = rand.randint( -dist, dist ), rand.randint( -dist, dist ) 
        
    _Dungeon.temple = ( rx,ry )
    
    # sub routine for item distribution
    def item_dist( _count, __Dungeon, _obj, _objs_whitelisted = False ):
    
        # account for list of whitelisted object positions
        objs_blacklisted = __Dungeon.objects

        if _objs_whitelisted:
            for obj in _objs_whitelisted:
                if obj in objs_blacklisted:
                    objs_blacklisted.remove(obj)
            
        for i in range( _count ):            
            x, y = __Dungeon.exit
            
            while (x,y) in objs_blacklisted or (x,y) == __Dungeon.exit: 
                x,y = __Dungeon.dungeon[ rand.randint(1, len(__Dungeon.dungeon)-1) ]     
                
            _obj.append( (x,y) )
            __Dungeon.objects.append( (x,y) )
            
        return __Dungeon, _obj
        
    per_tile = DUNGEON.SIZE_DEF / 100    
   
    _Dungeon, _Dungeon.chests   = item_dist( _DUNGEON.DISTRI_PERCENT["CHESTS"]  * per_tile, _Dungeon, _Dungeon.chests   )
    _Dungeon, _Dungeon.adve     = item_dist( _DUNGEON.DISTRI_PERCENT["ADVE"]    * per_tile, _Dungeon, _Dungeon.adve     )
    _Dungeon, _Dungeon.wizards  = item_dist( _DUNGEON.DISTRI_PERCENT["WIZARDS"] * per_tile, _Dungeon, _Dungeon.wizards  )
    _Dungeon, _Dungeon.monsters = item_dist( _DUNGEON.DISTRI_PERCENT["MONSTERS"]* per_tile, _Dungeon, _Dungeon.monsters )
    _Dungeon, _Dungeon.casinos  = item_dist( _DUNGEON.DISTRI_PERCENT["CASINOS"] * per_tile, _Dungeon, _Dungeon.casinos  )
    _Dungeon, _Dungeon.fungi    = item_dist( _DUNGEON.DISTRI_PERCENT["FUNGI"]   * per_tile, _Dungeon, _Dungeon.fungi    )
    
    # the only kind of object that can have overlap with another kind of object
    _Dungeon, _Dungeon.traps    = item_dist( _DUNGEON.DISTRI_PERCENT["TRAPS"]   * per_tile, _Dungeon, _Dungeon.traps, _Dungeon.chests )
    
    # DEBUG SHIT        
    print "c:",len(_Dungeon.chests), "a:",len(_Dungeon.adve), "w:",len(_Dungeon.wizards), "m",len(_Dungeon.monsters), "C",len(_Dungeon.casinos), "f",len(_Dungeon.fungi)        
            
    return _Dungeon
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  trade food and map info with a fellow adventurer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def meet_adve( _Player, _dung, _dung_chests  ):
                    
    FOOD_PER_GOLD   =  2
    FOOD_OFFER      = 50 + rand.randint( -10, 10 )  * rand.randint(0,1)
    FOOD_PRICE      = FOOD_PER_GOLD * FOOD_OFFER
    PICKAXE_PRICE   = 150 + rand.randint( -20, 20 ) * rand.randint(0,1)
    COMPASS_PRICE   = 120

    MAP_PRICE       = 100 + rand.randint( -20,20 )  * rand.randint(0,1)
    MAP_SIZE        = DUNGEON.SIZE_DEF / 20
    MAP_CHARS       = { "NOGROUND":'#', "GROUND":':', "PLAYER":'@', "CHEST":'$', "BORDER": '*' }
    
    print " (1) trade", FOOD_PRICE, "gold pieces for", FOOD_OFFER, "food rations"
    print " (2) see a piece of map for",MAP_PRICE,"gold pieces"
    if not _Player.pickaxe:
        print " (3) buy a pickaxe for", PICKAXE_PRICE
    if _Player.compass:
        print " (4) sell your compass for", COMPASS_PRICE
    print " (any other key to leave)"
    
    inp = raw_input(">> So, what is it?:")

    if inp == "1":
        if (_Player.gold >= FOOD_PRICE):
            _Player.gold -= FOOD_PRICE
            _Player.food += FOOD_OFFER
            print "Done. Gold left:", _Player.gold
        else:
            print "Not enough gold to buy the rations. You only have", _Player.gold, "gold."

    # draw a crude MAP_SIZE * MAP_SIZE map, the player in center. show gold too.
    elif inp == "2":
        if _Player.gold >= MAP_PRICE:
            _Player.gold -= MAP_PRICE
            print "Have a look at the surrounding area... @ = You, $ = Gold\n\n\t\t",
            
            for l in range( _Player.x - MAP_SIZE - 1, _Player.x + MAP_SIZE + 1 ):
                print MAP_CHARS["BORDER"],
                
            for y in range( _Player.y - MAP_SIZE, _Player.y + MAP_SIZE ):
                print "\n\t\t" + MAP_CHARS["BORDER"],
                for x in range( _Player.x - MAP_SIZE, _Player.x + MAP_SIZE ):
                    if (x,y) in _dung:
                        if (x,y) in _dung_chests:
                            print MAP_CHARS[ "CHEST" ],
                        elif (x,y) == ( _Player.x, _Player.y ):
                            print MAP_CHARS[ "PLAYER" ],
                        else:
                            print MAP_CHARS[ "GROUND" ],
                    else:
                        print MAP_CHARS[ "NOGROUND" ],
                print MAP_CHARS["BORDER"],
            
            print "\n\t\t",
            for l in range( _Player.x - MAP_SIZE - 1, _Player.x + MAP_SIZE + 1 ):
                print MAP_CHARS["BORDER"],
            print "\n"

        else:
            print "Not enough gold to see the map. You only have", _Player.gold, "gold."
    
    # buy a pickaxe
    elif inp == "3" and not _Player.pickaxe:
        if _Player.gold >= PICKAXE_PRICE:
            _Player.gold -= PICKAXE_PRICE
            print "Wow. A brand new PICKAXE! Now you can digg through walls!"
            _Player.pickaxe = True
        else:
            print "Not enough gold to buy this item. You only have", _Player.gold, "gold."
    
    elif inp == "4" and _Player.compass:
        _Player.compass = False
        _Player.gold   += COMPASS_PRICE
        print "You sold your compass."
    
    else:
        print "- No recognized option. Moving on."

    return _Player

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  talk to a wizard to get an inv potion and more dungeon info
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def meet_wizard( _Player, _Dungeon ):

    SECRET_PRICE = 25  + rand.randint(  -5,  5 ) * rand.randint(0,1)
    INV_PRICE    = 100 + rand.randint( -20, 20 ) * rand.randint(0,1)

    print " So you talk to the wizard..."
    print " (1) He will tell you a random secret for", SECRET_PRICE, "food rations"
    print " (2) Give you a potion of invisibility for", INV_PRICE, "gold pieces"
    print " (Any other key to leave)"
    
    inp = raw_input("- So, what is it?:")
    
    if inp == "1":
        if _Player.food >= SECRET_PRICE:
            _Player.food -= SECRET_PRICE
     
            answer = rand.randint(0,3)
            if answer == 0:
                print "'Alright then. Let me think...'"
                print "- Here are the coordinates of all treasure chests in the dungeon:"
                for i in _Dungeon.chests:
                    print " +", i
            elif answer == 1:
                print "'Mhmmm. Do you know where the exit is?' It is at", _Dungeon.exit
            elif answer == 2:
                print "- He tells you about traps and where they are:'"
                for i in _Dungeon.traps:
                    print " +", i
            else:
                print "- 'Once, I stole a cookie! Shameful, I know.'" 
                print "- Bummer, hopefully, he'll tell me a real secret next time."
        else:
            print "- You don't have enough food for this."
    
    elif inp == "2":
        if not _Player.potion_inv:
            if _Player.gold >= INV_PRICE:
                _Player.potion_inv = True
                _Player.gold -= INV_PRICE
                print "- You aquired an INVISIBILITY potion! This will be useful to bypass monsters."
            else:
                print "- You don't have enough money to buy it!"
        else:
            print "- You already have a potion of that kind!"
    
    else:
        print "- no sensible option chosen. Moving on."
            
    return _Player

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Terrible things are about to happen
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def meet_monster( _Player, _dung_monsters ):

    # inv potion? No dice. ;)
    if _Player.potion_inv:
        print "- You use your potion of invisibility. The monster can't see you."
        print "- You sneak around it and steal its rune. The monster disappears!"
        _Player.potion_inv = False
        _Player.runes += 1
        _dung_monsters.remove( (Player.x, Player.y) )
        return _Player, _dung_monsters

        
    DICE_COUNT    = 3
    guesses_left  = DICE_COUNT + 1
    dice          = []
    
    for i in range( DICE_COUNT ):
        dice.append( rand.randint(1,6) )
    
    print "The monster challenges you to a game of guess-my-dice!"
    print "It says: 'Rolled 3 dice. The sum of their pips is", sum(dice)
    print "Guess the individual pips of my dice!",
    print "You can answer", guesses_left, "times!'"
    
    for i in range( len(dice) ):
        dice[i] = str( dice[i] )
    
    while ( guesses_left > 0 and dice != [] and guesses_left >= len(dice) ):
        inp = raw_input( ">> Answer? [1,2,3,4,5 or 6]:" )
        if inp in dice:
            dice.remove( inp )
            print "> Correct!"
            if dice != []: 
                print str( len(dice) ) + " left to guess."
        else:
            print "> WRONG!"
            guesses_left -= 1            
    
    if dice == []:
        print "You win!"
        print "- The monster is intrigued and hands you a RUNE!"
        print "- The monster disappears in a puff of smoke!"
        _dung_monsters.remove( (_Player.x,_Player.y) )
        _Player.runes += 1
    else:
        print "You LOST! Dice left: ", dice
        print "- The monster is victorious! You lose 1/2 of your gold and 1/2 of your food!"
        _Player.gold /= 2
        _Player.food /= 2
        
    return _Player, _dung_monsters

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Too much money? We can help!
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def enter_casino( _Player, _Dungeon ):

    SESSION_PRICE = 5 + rand.randint( -2, 2 )
    SLOT_COUNT    = 3
    slot_elements = [ "APPLE", "COIN", "???" ]
    WON_FOOD, WON_GOLD = 50, 50

    print "- Entered the casino. Here are a couple of big slot machines,"
    print "  that you can play for", SESSION_PRICE, "gold pieces per session."
    print "- You have to play at least once.\n"
        
    inp = "y"
    
    while _Player.gold >= SESSION_PRICE and inp == "y":
    
        slot_result = []
        for i in range( SLOT_COUNT ):
            slot_result.append( slot_elements[ rand.randint(0, len(slot_elements)-1 ) ] )
    
        print "* result: [" + " <> ".join( slot_result ) + "]"
    
        if   slot_result.count( slot_elements[ 0 ] ) == SLOT_COUNT:
            print "* You won a box of apples. Congratulations!"
            _Player.food += WON_FOOD
        elif slot_result.count( slot_elements[ 1 ] ) == SLOT_COUNT:
            print "* You won some change!"
            _Player.gold += WON_GOLD
        elif slot_result.count( slot_elements[ -1 ] ) == SLOT_COUNT:
            print "* You won a scroll. It seems useless, but someone scribbled some coordinates"
            print "  on this piece of paper."
            print "  ???:", _Dungeon.temple
        else:
            print "- You win absolutely nothing. You lost some money though."
            
        _Player.gold -= SESSION_PRICE
        
        inp = raw_input("\n>> Want to play another round? (" + str(_Player.gold) + " gold coins left) (y/n):")
    
    # you have to go
    if inp == "y":
        print "- Sorry pal, no money left to waste!"
    else:
        print "- Ok then, moving on."
    
    return _Player

    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  you can change the default dungeon size via command line option
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
try:
    if len( sys.argv ) == 2:
        if int( sys.argv[1] ) in range( DUNGEON.SIZE_MIN, DUNGEON.SIZE_MAX ):
            DUNGEON.SIZE_DEF = int( sys.argv[1] )
            print "* Default dungeon size changed to:", DUNGEON.SIZE_DEF
        else:
            print "* Dungeon size can only between", DUNGEON.SIZE_MIN, "and", DUNGEON.SIZE_MAX
except:
    print "* Command line parameter looks all messed up and is therefore being ignored"
    print "* To change the default dungeon size, start the script with \"pytarl.py [SIZE]\""
    print "  where SIZE is an integer between", DUNGEON.SIZE_MIN, "and", DUNGEON.SIZE_MAX
    
  
Dungeon = create_dungeon( DUNGEON.SIZE_DEF, Dungeon, DUNGEON )

running  = True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ...and off we go
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print "\nWelcome to " + APP_NAME + " (" + APP_VERSION + "/" + sys.platform + ")"
print "Find the mysterious and ancient golden idol and make it to the exit alive!"
print "And find some gold, while you at it!",
print "Enter '?' at the prompt for more help!"


while( running ):

    # give a hint where to find the exit
    if Player.compass:
        dist_exit = ( abs(Player.x - Dungeon.exit[0]), abs(Player.y - Dungeon.exit[1]) )
    else:
        dist_exit = "-" 
        
    # detect a near-by trap
    traps_nearby = int(( Player.x+1, Player.y )   in Dungeon.traps) + int(( Player.x-1, Player.y )   in Dungeon.traps) + \
                   int(( Player.x,   Player.y+1 ) in Dungeon.traps) + int(( Player.x,   Player.y-1 ) in Dungeon.traps)
        
    # basic info
    if sys.platform == "win32":
        CHAR_SEP = chr(175)
    else:
        CHAR_SEP = "~"
        
    # display fungi load if needed
    if Player.fungi_load:
        FUNGI_LOAD = "(+" + str( Player.fungi_load ) + ")"
    else:
        FUNGI_LOAD = ""

    print "\nfood:", Player.food, FUNGI_LOAD, CHAR_SEP, "gold:", Player.gold, CHAR_SEP, "compass:", \
          dist_exit, CHAR_SEP, "position:", ( Player.x, Player.y ), CHAR_SEP, "traps:", traps_nearby   
          
    # fungi side effect: trap awareness
    if Player.fungi_load in range( DUNGEON.FUNGI_ADDLOAD, Player.FUNGI_MAX + 1 ):
        print "~ Due to high fungi intoxination, you can detect traps..",
        if traps_nearby: 
            if (Player.x, Player.y-1) in Dungeon.traps:
                print "north..",
            if (Player.x, Player.y+1) in Dungeon.traps:
                print "south..",
            if (Player.x+1, Player.y) in Dungeon.traps:
                print "east..",
            if (Player.x-1, Player.y) in Dungeon.traps:
                print "west..",
            print
        else:
            print "but there are none."
    
    # key that will always be needed     
    keys = [ KEY_HELP, KEY_NOMOVE, KEY_INFO ]
    # add fungi key if needed too   
    if Player.fungi:
        keys += [KEY_FUNGI]    
    # where can we move to?
    if (Player.x, Player.y - 1) in Dungeon.dungeon:
        keys += [KEY_NORTH]
    if (Player.x, Player.y + 1) in Dungeon.dungeon:
        keys += [KEY_SOUTH]
    if (Player.x + 1, Player.y) in Dungeon.dungeon:
        keys += [KEY_EAST]
    if (Player.x - 1, Player.y) in Dungeon.dungeon:
        keys += [KEY_WEST]
        
    # console input
    key = raw_input( ">> [" + "/".join(keys) + "]:" )
    
    # show help/info
    while key in KEYS_MISC or key in ["help","Help","HELP"]:
        if key == KEY_HELP or key in ["help","Help","HELP"]:
            show_help()
        elif key == KEY_INFO:
            show_info( Player, Dungeon )
        key = raw_input( ">> [" + "/".join(keys) + "]:" )
    
    # emergency exit
    if key in ["exit","EXIT","quit","QUIT"]:
        print "- Programm Termination."
        running = False
    
    # fungi! don't eat those.
    elif key == KEY_FUNGI and key in keys:
        print "- So, you decided to eat a collected fungus"
        Player.fungi      -=  1
        Player.fungi_load += DUNGEON.FUNGI_ADDLOAD
        if Player.fungi_load > Player.FUNGI_MAX:
            Player.fungi_load = Player.FUNGI_MAX
            print "- Due to extra high levels of fungi intoxination, your vision became all blury"
            print "  For some hours you were giggling like a five year old"
            print "  ...and you had a vision... about a hidden temple near", \
                (Dungeon.temple[0] + rand.randint(-2, 2), Dungeon.temple[1] + rand.randint(-2, 2))
    
    # let's move...
    elif key in KEYS_MOVE and key in keys:
        
        if key == KEY_NOMOVE:
            # ...unless we don't. let's rest and check for monsters
            print "- You inspect your surroundings... ",
            monsters_nearby = {}
            monsters_nearby["N"] = ( Player.x, Player.y-1 ) in Dungeon.monsters
            monsters_nearby["S"] = ( Player.x, Player.y+1 ) in Dungeon.monsters
            monsters_nearby["E"] = ( Player.x+1, Player.y ) in Dungeon.monsters
            monsters_nearby["W"] = ( Player.x-1, Player.y ) in Dungeon.monsters
            
            if any( monsters_nearby.values() ):
                
                if sum( monsters_nearby.values() ) > 1:
                    monsters_str = "monsters to the "
                else:
                    monsters_str = "a monster to the "
                
                if monsters_nearby["N"]:
                    monsters_str += "north.. "
                elif monsters_nearby["S"]:
                    monsters_str += "south.. "
                elif monsters_nearby["E"]:
                    monsters_str += "east.. "
                elif monsters_nearby["W"]:
                    monsters_str += "west.. "
                print monsters_str
                
            else:
                print "no monsters around!"
                
        xd, yd = KEYS_MOVE[ key ]
        Player.x += xd
        Player.y += yd
        Player.turns += 1
        
        if not Player.fungi_load:
            Player.food  -= 1
        else:
            Player.fungi_load -= 1
        
        if (Player.x, Player.y) not in Dungeon.visited:
            Dungeon.visited.append( (Player.x, Player.y) )
    
    # no go? we can still digg our way out
    elif key in KEYS_MOVE:
        if Player.pickaxe:
            xd, yd = KEYS_MOVE[ key ]
            Dungeon.dungeon.append( (Player.x + xd, Player.y + yd) )
            print "- You swing your pickaxe. There: A new pathway!"
            # the longer you use it, the more likely it breaks
            if Player.pickaxe_use > 0 and \
               rand.randint( 0, Player.PICKAXE_DURABILITY - Player.pickaxe_use ) == 0: 
                print "- DANG! Your axe broke. It's useless now."
                Player.pickaxe = False
            Player.pickaxe_use += 1
        else:
            print "Can't go that way! Solid walls. There might be a way to destroy those."
    else:
        print "! No recognized command. Try entering '" + KEY_HELP + "' for the help page!"
    
    pos = ( Player.x, Player.y )

    # fungus?
    if pos in Dungeon.fungi:
        print "- Here's are some strange fungus growing. You rip it off and take it with you."
        print "- Although they seem edible, you heard of strange, outlandish side effects..."
        print "- Press '" + KEY_FUNGI + "' to eat one of your collected fungi."
        Player.fungi += 1
        Dungeon.fungi.remove( (Player.x, Player.y) )
    
    # found some gold?
    if pos in Dungeon.chests:
        Player.gold += rand.randint( 10, 100 )
        print "- You found some gold! You now have", Player.gold, "pieces!"
        Dungeon.chests.remove( (Player.x, Player.y) )
        print "- Treasures left in this dungeon: " + str( len( Dungeon.chests ) );
        
    # meeting a fellow adventurer?
    if pos in Dungeon.adve:
        print "\n- A fellow Adventurer is nearby!"
        Player = meet_adve( Player, Dungeon.dungeon, Dungeon.chests )

    # meeting a strange wizard?    
    if pos in Dungeon.wizards:
        print "\n- A wizard is nearby!"
        Player = meet_wizard( Player, Dungeon )

    # "meeting" a monster?
    if pos in Dungeon.monsters:
        print "\n- You stepped on the turf of a monster! Prepare for gruesome things to happen!\n"
        Player, Dungeon.monsters = meet_monster( Player, Dungeon.monsters )
    
    # found the temple?
    if pos in Dungeon.temple:
        print "\n- You found the hidden temple!"
        Player.temple_seen = True
        if Player.runes in range( 1, TEMPLE.RUNES_WANTED ):
            print "- You have not enough runes to receive your reward."
        else:
            print "- Since you have brought all", TEMPLE.RUNES_WANTED, "runes back to the temple",
            print "you receive your reward!"
            gold += rand.randint( TEMPLE.REWARD_MIN, TEMPLE.REWARD_MAX )
            print "- You get a GOLDEN IDOL and some pocket change."
            Player.idol  = True
            Player.runes = 0
    
    # found casino?
    if pos in Dungeon.casinos:
        inp = raw_input( ">> You found a casino! They advertise their magic slot machine. Go in? (y/n):" )
        if inp == "y":
            Player = enter_casino( Player, Dungeon )
        else:
            print "- Alright. Moving on."

    # "found" a trap?
    if pos in Dungeon.traps:
        print "- You walked right into a devious dungeon trap!"
        print "  It takes a long time to heal those wounds! You could disable the trap though." 
        print "  For a time, you could not move, but had to eat anyway."
        Player.food  -= DUNGEON.TRAP_PENALTY
        Player.turns += DUNGEON.TRAP_PENALTY
        Dungeon.traps.remove( (Player.x, Player.y) )
            
    # happy end!
    if pos == Dungeon.exit:
        print "- Exit found!"
        inp = raw_input(">> Do you want to go? (y/n)")
        if inp == "y":
            print "- Turns:", Player.turns
            running = False
            if Player.gold > 0:
                print "- Gold:", Player.gold, 
                if len( Dungeon.chests ) == 0:
                    print "(You found all the treasures. Congratulations!)"
            else:
                print "- You did not find any gold!"
            if Player.idol:
                print "- You escaped with the GOLDEN IDOL!"
            else:
                print "- You did not find the golden idol."
            score = Player.gold                                   \
                    + Player.runes            * SCORE.RUNES       \
                    + int(Player.pickaxe)     * SCORE.PICKAXE     \
                    + int(Player.temple_seen) * SCORE.TEMPLE_SEEN \
                    + int(Player.idol)        * SCORE.IDOL        \
                    + Player.food             * SCORE.FOOD        \
                    + int(Player.potion_inv)  * SCORE.POTION_INV  \
                    + Player.turns            * SCORE.TURNS 
            print "- Score:", score  
        else:
            print "Ok, then. Moving on."
    
    # check your goods
    if Player.food <= 0:
        print "!! No food left! You have to end your journey, before you starve to death!"
        running = False
    elif Player.food < 10:
        print "!! You don't have many food rations left!"
        
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  famous last word(s)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print "\nBye. Thank you for playing " + APP_NAME + "." 
raw_input("\n[Hit Enter to Exit]")
