

class StatBar:
    def __init__(self,parent):
        self.bar = parent
        self.items = {}

    def append(self,name,val):
        self.items[name] = val
        self.show()

    def show(self):
        str = ''
        for key in self.items:
            str += " {0} - '{1}' |".format(key,self.items[key])
            self.bar.setText(str[:len(str)-1])