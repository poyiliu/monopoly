from random import shuffle as reorder
from operator import attrgetter


#typer and colors
UTILITY = "UTILTIES"
RW_STATION = "RAILWAY STATIONS"
INDIGO = "INDIGO COLOR" # or whatever this color is #171363
WHITE = "WHITE COLOR"
PURPLE = "PURPLE COLOR"
ORANGE = "ORANGE COLOR"
RED = "RED COLOR"
YELLOW = "YELLOW COLOR"
GREEN = "GREEN COLOR"
BLUE = "BLUE COLOR"
NOPLAYER = "I'm no body"
JAIL="JAIL"
#this class represents a deck of cards like surprize cards or punishment cards
board=None
players=[]
console = -1
###########################################################################
#dont forget to set this before each game
def init_state(newPlayers,newBoard,newConsole):
    global players,board,console
    players,board,console=newPlayers,newBoard,newConsole
########################################################################
def getAmount(aType):
    counter=0
    for block in board.blocks:
        if block.color==aType:
            counter+=1
    return counter            
    
def getPlayerFromName(name):
    for player in players:
        if player.name==name:
            return player
    return None    
###################
# Cards Section
###################

class deck():
    def __init__(self,cards,name):
        self.name=name
        self.cards=cards
        self.discard=[]
    def shuffle(self):
        """Rearranging cards and shuffling"""
        reorder(self.cards)     #importing shuffle as reorder
        
    def getCard(self):      #getting a card from the deck        
        if len(self.cards)==0:            
            self.cards=self.discard
            self.shuffle()
            self.discard=[]            
        card = self.cards.pop()
        self.discard.append(card)
        return card
    
    def addCard(self, card):
        self.cards.append(card)
        
        
class card():
    '''this class represent a card
       a card have a titile,text variables and applyToPlayer function
    '''
    def __init__(self,title,text):
        self.title=title
        self.text=text
        
    def applyToPlayer(self,player):
        pass

class changeMoneyCard(card):
    '''this card can incrase or decrease the player money
       also it could depened on all the players(commune)
    '''
    def __init__(self,title,text,amount,commune=False):
        card.__init__(self,title,text)
        self.commune=commune
        self.amount=amount # amount of money to add or subtract from player(positive value will add and negetive will subtract)
        #change from fork
    def applyToPlayer(self,player):
        if self.commune:        
            for p in players:
                if p.name!=player.name:
                    player.money+=self.amount
                    p.money-=self.amount
                    if self.amount>0:
                        console.display(player.name+" got "+str(self.amount)+" from "+p.name)
                    else:
                        console.display(player.name+" paid $"+str(-1*self.amount)+" to "+p.name)
        else:            
            player.money+=self.amount
            if self.amount>0:
                console.display(player.name+" got $"+str(self.amount)+" from bank")
            else:
                console.display(player.name+" paid $"+str(-1*self.amount)+" to bank")
class advanceToCard(card):
    def __init__(self,title,text,target,applyGo=True):
        card.__init__(self,title,text)
        self.targetName=target
        self.applyGo=applyGo
        if target==JAIL or target=='GO!':
            self.applyGo=False
    
    def applyToPlayer(self,player):
        loc=player.location        
        while board.blocks[loc].name!=self.targetName:            
            loc=(loc+1)%len(board.blocks)
            if self.applyGo:
                if loc==0:
                    player.money+=200
                    console.display("player went through start got 200")        
        player.landOn(board.blocks[loc],loc)
        if self.targetName==JAIL:
            player.inJail=True
            player.jailCounter=0
        actions=board.blocks[loc].getActions()
        if(len(actions)==1):
            for key in actions.keys():
                actions[key]()
        else:
            self.console.chooseFromOptions(actions)                


class moveToNearestCard(card):
    def __init__(self,title,text,targetColor,applyGo=True):
        card.__init__(self,title,text)
        self.color=targetColor 
    def applyToPlayer(self,player):
        loc=player.location
        
        while board.blocks[loc].color!=self.color:            
            loc=(loc+1)%len(board.blocks)
            if self.applyGo:
                if loc==0:
                    player.money+=200
                    console.display("player went through start got $200")        
        player.landOn(board.blocks[loc],loc)
        actions=board.blocks[loc].getActions()
        if(len(actions)==1):
            for key in actions.keys():
                actions[key]()
        else:
            self.console.chooseFromOptions(actions)

###################
# Blocks Section
###################


#represents a block on the board that containing an asset
#this block can belong to a player
class block():
    def __init__(self, name):
        self.name = name
    def pass_(self):
        pass
    def getActions(self):
        pass
    
class utilBlock(block):         #utilities and railway stations
    def __init__(self, name, uType, price):
        block.__init__(self, name)
        self.color = uType    #utiltiy or railway station !see top at the file
        self.price = price
        self.owner=None
    def __str__(self):
        return self.name + " of " + self.color
    
    def __repr__(self):
        return self.name + " of " + self.color
     
    
    def pay_rent(self):        
        if self.color==RW_STATION:
            player=getPlayerFromName(self.owner)
            num=player.howMany(RW_STATION)
            rent=25*(2**(num-1))
        else:            
            player=getPlayerFromName(self.owner)
            diceRoll=self.player.getLatestRoll()
            num=player.howMany(RW_STATION)
            if num==1:
                rent=4*diceRoll
            elif num==2:
                rent=10*diceRoll
        console.display(self.player.name+" pay rent of "+str(rent)+" to "+self.owner)
        self.player.pay(rent)
        getPlayerFromName(self.owner).money+=rent
    def purchase(self):
        if not self.player==NOPLAYER:
            if self.player.money >= self.price:
                self.player.buy(self)
                console.display("{} bought the {} for ${}".format(self.player.name,str(self),self.price))
            else:    
                console.display("{} don't have ${} to buy {}".format(self.player.name,self.price,str(self)))        
    def getActions(self):
        if self.owner==None :
            return {"buy":self.purchase,"pass":self.pass_}            
        elif self.owner==self.player.name or self.owner=='bank':                        
            return {"pass":self.pass_}
        else:
            return {"payrent":self.pay_rent()}                            
    def mortage(self):
        if(self.owner!='bank' and self.owner!=None):
            #player=getPlayerFromName(self.owner)
            player.money+=self.price/2
            self.owner='bank'
    def reMortage(self,player):
        if self.owner=='bank':
            player.buy(self)
        

class assetBlock(block):
    def __init__(self,name,color,price):
        block.__init__(self,name)        
        self.color=color
        self.price=price
        self.houses=0
        self.hotel=False
        self.owner=None
        
    def __str__(self):
        return self.name + " of " + self.color
    
    def __repr__(self):
        return self.name + " of " + self.color
    
    def pay_rent(self):
        rent=self.price//30
        self.player.pay(rent)
        getPlayerFromName(self.owner).money+=rent
        console.display(self.player.name+" paid rent of "+str(rent)+" to "+self.owner)
    
    def getActions(self):
        if self.owner==None :
            return {"buy":self.purchase,"pass":self.pass_}            #auction???
        elif self.owner==self.player.name or self.owner=='bank':                        
            return {"pass":self.pass_}
        else:
            return {"payrent":self.pay_rent}                        
    
    def purchase(self):            #buy function should not exist, whole process should be in purchase
        if not self.player==NOPLAYER:       #And believe me is against principles! both classes are mutuly dependent, 
            if self.player.money >= self.price:     
                self.player.buy(self)           #only one class should be calling other class!
                console.display("{} bought the {} for ${}".format(self.player.name,str(self),self.price))
            else:    
                console.display("{} don't have ${} to buy {}".format(self.player.name,self.price,str(self)))
                
    def mortage(self):
        if(self.owner!='bank' and self.owner!=None):
            #player = getPlayerFromName(self.owner)
            player.money+=self.price/2
            self.owner='bank'
    def reMortage(self,player):
        if self.owner=='bank':
            player.buy(self)
    def buildHouse(self):
        pass
    def buildHotel(self):
        pass


#represent a block on the board that landing on means u need to pull a card from some deck        
class cardBlock():
    def __init__(self, name,deck):
        block.__init__(self, name)
        self.deck=deck
    def getCard(self):
        card=self.deck.getCard()
        console.display(self.player.name+" got Card : "+card.title+" , "+card.text)
        card.applyToPlayer(self.player)
    def getActions(self):
        return {"getcard":self.getCard}
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

class moneyBlock():                 #Go , tax , luxury tax etc blocks which onLand
    def __init__(self, name, money):      # action is just adding or subtracting money
        block.__init__(self, name)
        self.deck=deck
        self.money = money
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def use(self):
        if not self.player==NOPLAYER:
            self.player.money+=self.money
            if self.money > 0:
                console.display("{} got ${} salary from {}".format(self.player.name,self.money,self.name))
            elif self.money < 0:
                console.display("{} paid ${} {}".format(self.player.name,self.money*-1,self.name))
    def getActions(self):
        return {"changemoney : "+str(self.money):self.use}
    
    
class goToJailBlock(block):
    def __init__(self, name="'Go TO Jail'"):
        block.__init__(self, name)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

    def goToJail(self):
        console.display(self.player.name+ ", go to jail!")
        if not self.player==NOPLAYER:
            self.player.goToJail()
    def getActions(self):
        return {'Go To jail':self.goToJail}
               


##################
# Player Section
##################


#represent a player
#player attributes : name,money,location,assets        
class player():
    
    def __init__(self,name,money):
        self.name=name
        self.money=money
        self.assets={}
        self.location=0
        self.getOutOfJailCard=False
        self.inJail=False
        
    def pay(self,ammount):
        self.money-=ammount
        
    def buy(self,assetBlock):
        self.money-=assetBlock.price
        assetBlock.owner=self.name
        if(assetBlock.color in self.assets):
            self.assets[assetBlock.color].append(assetBlock)
        else:
            self.assets[assetBlock.color]=[assetBlock,]
    def printPlayer(self):
        console.display(self.name+" has money: "+str(self.money)+" and assets : "+str(self.assets))
        
    def landOn(self,block,location):        
        self.location=location
        block.player=self
        console.display(self.name+" lands on "+ str(block))
        
    def getHousesAndHotels(self):
        houses=0
        hotels=0
        for group in self.assets.values():
            for asset in group:
                houses+=asset.houses
                if asset.hotel==True:
                    hotels+=1
        return (houses,hotels)    
    def inc_jail_count(self):
        self.jailCounter+=1
        if self.jailCounter>=3:
            self.inJail=False
    def goToJail(self):
        self.inJail=True
        self.jailCounter=0
        while board.blocks[self.location].name!=JAIL:            
            self.location=(self.location+1)%len(board.blocks)
    def howMany(aType):
        if aType in assets:
            return len(assets[aType])
        else:
            return 0
    def buyHouse(self,block):
        if block.owner==self.name:
            if block.color!=UTILITY and block.color!=RW_STATION:
                if self.howMany(block.color)==getAmount(block.color):
                    if block.houses<4:
                        block.houses+=1
                        self.pay(150)
    
    def is_bankrupt(self):
        if self.money<=0:
            return True
        return False
    def updateRoll(self,roll):
        self.latestRoll=roll
    def getLatestRoll(self):
        return self.latestRoll
