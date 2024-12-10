"""
    Class that represents the links between atoms
    For now the links works by just checking if an atom is primary or not
    and if the first parameter matches with a primary atom parameter
    

"""

class Links:
    def __init__(self, links):
        self.links = links[0]
        self.primary_atoms = self.links.keys()

    """
        check if whether an atom is primary or not
    """
    def isPrimary(self, atomHead):
        return atomHead in self.primary_atoms
    
    """
        check if whether an atom is linked or not to a primary atom
        returns the primary atom if linked, else None
    """
    def isLinked(self, atomHead):
        for primary_atom in self.primary_atoms:
            if atomHead in self.links[primary_atom]:
                return primary_atom
        return None
            
