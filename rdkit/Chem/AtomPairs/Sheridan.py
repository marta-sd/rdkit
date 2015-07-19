#
#  Copyright (C) 2015 Greg Landrum
#
#   @@ All Rights Reserved @@
#  This file is part of the RDKit.
#  The contents are covered by the terms of the BSD license
#  which is included in the file license.txt, found at the root
#  of the RDKit source tree.
#
""" Contains an implementation of Physicochemical property fingerprints, as
described in:
Kearsley, S. K. et al.
"Chemical Similarity Using Physiochemical Property Descriptors."
J. Chem.Inf. Model. 36, 118-127 (1996)
"""
from rdkit.DataStructs import IntSparseIntVect
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import DataStructs

from rdkit.Chem.rdMolDescriptors import GetAtomPairFingerprint,GetHashedAtomPairFingerprint
GetAtomPairFingerprintAsIntVect=rdMolDescriptors.GetAtomPairFingerprint

numPathBits=rdMolDescriptors.AtomPairsParameters.numPathBits
_maxPathLen=(1<<numPathBits)-1
numFpBits=numPathBits+2*rdMolDescriptors.AtomPairsParameters.codeSize
fpLen=1<<numFpBits

import os.path,re
from rdkit import RDConfig
def _readPattyDefs(fname=os.path.join(RDConfig.RDDataDir,'SmartsLib','patty_rules.txt')):
    with open(fname,'r') as inf:
        lines = [x.strip().split('# ')[0].strip() for x in inf]
    splitl = [re.split('[ ]*',x) for x in lines if x != '']
    matchers = []
    for tpl in splitl:
        if len(tpl)>1:
            mol = Chem.MolFromSmarts(tpl[0])
            if mol is None:
                continue
            nm = tpl[1]
            matchers.append((mol,nm))
    return matchers

_pattyDefs=None
def AssignPattyTypes(mol,defns=None):
    """

    >>> from rdkit import Chem
    >>> AssignPattyTypes(Chem.MolFromSmiles('OCC(=O)O'))
    ['POL', 'HYD', 'OTH', 'ANI', 'ANI']

    """
    global _pattyDefs
    if defns is None:
        if _pattyDefs is None:
            _pattyDefs = _readPattyDefs()
        defns = _pattyDefs
    res = ['']*mol.GetNumAtoms()
    for matcher,nm in defns:
        matches = mol.GetSubstructMatches(matcher,uniquify=False)
        for match in matches:
            res[match[0]] = nm
    return res

typMap=dict(CAT=1,ANI=2,POL=3,DON=4,ACC=5,HYD=6,OTH=7)
def GetBPFingerprint(mol,fpfn=GetAtomPairFingerprint):
    """
    >>> from rdkit import Chem
    >>> fp = GetBPFingerprint(Chem.MolFromSmiles('OCC(=O)O'))
    >>> fp.GetTotalVal()
    10
    >>> nze=fp.GetNonzeroElements()
    >>> sorted([(k,v) for k,v in nze.items()])
    [(32834, 1), (49219, 2), (98370, 2), (98401, 1), (114753, 2), (114786, 1), (114881, 1)]
    
    """
    typs = [typMap[x] for x in AssignPattyTypes(mol)]
    fp = fpfn(mol,atomInvariants=typs)
    return fp
                
        
        
        
#------------------------------------
#
#  doctest boilerplate
#
def _test():
  import doctest,sys
  return doctest.testmod(sys.modules["__main__"])


if __name__ == '__main__':
  import sys
  failed,tried = _test()
  sys.exit(failed)
  
  

