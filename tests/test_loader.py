#!/usr/bin/python
#
# This code serves as a testing harness for the Pygr source tree. 
# If your tarball is fresh out of CVS, and a test fails, please 
# forward stdout to <leec@ucla.edu> so issues can
# can be addressed in a timely fashion. Thank you!

import os
import sys
import re

class TestMain(object):

   def __init__(self):

      self.environ = os.environ # Get OS dependent constants
      self.linesep = os.linesep
      self.name = os.name 
      self.path = sys.path
      self.ver = sys.version.split(" ")[0][0:3]
      self.platform = sys.platform
      self.__doc__ = "Testing Framework for the Pygr source tree."
 
      try:
         self.path.append(os.environ['PYGRPATH']) # Add src tree to search path 

      except KeyError:  
	 print "$PYGRPATH is not set. Trying next method...\n"
         self.path.append(os.getcwd()[:-6]+"/pygr")

      try:
 	import mapping
	import graphquery 
        self.mapping = mapping
	self.graphquery = graphquery 
      except:
         raise ImportError("Unable to load Pygr modules. Set PYGRPATH accordingly.") 

      try:
         import unittest
	 self.unittest = unittest
      except:
         if  (float(self.ver) < 2.1):
           raise ImportError("Python %s does not come with unittest. Install the module or upgrade python" %(self.ver))
         else:
            raise ImportError("Unable to load unittest module.")
      
   def __debug__(self):
      print "SYS PATH: " + str(self.path) 
      print "environ: " + str(self.environ)
      print self.linesep + "linesep: " + str(self.linesep)
      print self.linesep + "name: " + str(self.name)         
      print self.linesep + str(os.path)

class TestFrameWork(TestMain):

  
   def go(self):

     print "Initializing Test Framework...\n"

     unittest = self.unittest
     mapping = self.mapping
     graphquery = self.graphquery


     class QuerySuite(unittest.TestCase):

        __doc__ = "Pygr Query tests..."
  
        def setUp(self):

	   self.result_kounter = 0

        def dqcmp(self,datagraph,querygraph,result):

 
           for i in graphquery.GraphQuery(datagraph,querygraph):
    
              if (result != {}):
                 self.failUnless(i == result[self.result_kounter], 'incorrect result')
                 self.result_kounter += 1 
              else:
                 try: 
                    if(i):
                       empty_set = False 
                 except:
                    empty_set = True

                 self.failUnless(empty_set)
         
        def testBasicQuery(self):  # Basic Query Test

 	   datagraph = {0: {1: None, 2: None, 3: None}, 1: {2:None}, 3: {4: None, 5: None}, 4: {6: None}, 5: {6: None}, 2: {}, 6: {}}

           querygraph = {0: {1: None, 2: None, 3: None}, 3:{4: None},1:{},2:{},4:{}}

           result = {0: {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}, 1: {0: 0, 1: 1, 2: 2, 3: 3, 4: 5}, 2: {0: 0, 1: 2, 2: 1, 3: 3, 4: 4}, 3: {0: 0, 1: 2, 2: 1, 3: 3, 4: 5}}     

           self.dqcmp(datagraph,querygraph,result)
 
        def testCyclicQuery(self): # Test cyclic QG against cyclic DG 


           datagraph = {1:{2:None},2:{3:None},3:{4:None},4:{5:None},5:{2:None}}
           querygraph = {0:{1:None},1:{2:None},2:{4:None},3:{1:None},4:{3:None}}
	   result = {0: {0: 1, 1: 2, 2: 3, 3: 5, 4: 4}}
	   self.dqcmp(datagraph,querygraph,result)

        def testCyclicAcyclicQuery(self): # Test cyclic QG against acyclic DG 

           datagraph = {0:{1:None},1:{3:None},5:{3:None},4:{5:None},2:{4:None,1:None},3:{}}
          
           querygraph = {0:{1:None},1:{3:None},3:{5:None},5:{4:None},4:{2:None},2:{1:None}}

	   result = {}

           self.dqcmp(datagraph,querygraph,result)

        def testSymmetricQuery(self): # Test symmetrical QG against symmetrical DG

           datagraph = {1:{2:None},2:{3:None,4:None},5:{2:None},3:{},4:{}}
           querygraph = {0:{1:None},1:{2:None},2:{}}
           result = {0: {0: 1, 1: 2, 2: 3}, 1: {0: 1, 1: 2, 2: 4}, 2: {0: 5, 1: 2, 2: 3}, 3: {0: 5, 1: 2, 2: 4}}

	   self.dqcmp(datagraph,querygraph,result)

        def testFilteredQuery(self): # Test a filter against a query

           datagraph = {0: {1: None, 2: None, 3: None}, 1: {2: None, 3: None}, 3: {4: None}}

	   querygraph = {0:{1:{'filter':lambda toNode,**kw:toNode == 3}},1:{}}
           result = {0:{0: 0, 1: 3},1:{0: 1, 1: 3}}

           self.dqcmp(datagraph,querygraph,result)
			

	def testHeadlessQuery(self): # Test a query with no head nodes

           datagraph = {0:{1:None},1:{2:None},2:{3:None},3:{4:None},4:{1:None}}
	   querygraph = {0:{1:None},1:{2:None},2:{3:None},3:{0:None}}
  
           result = {0:{0: 1, 1: 2, 2: 3, 3: 4},\
		     1:{0: 2, 1: 3, 2: 4, 3: 1},\
	             2:{0: 3, 1: 4, 2: 1, 3: 2},\
		     3:{0: 4, 1: 1, 2: 2, 3: 3}}

          
           self.dqcmp(datagraph,querygraph,result)


     class MappingSuite(unittest.TestCase):
  
        __doc__ = "Pygr Mapping tests..." 

	def setUp(self):
          
	   self.datagraph = mapping.dictGraph()
           
        def testGraphDict(self):
       
           datagraph = self.datagraph
           datagraph += 1 
           datagraph[1] += 2,3 
           results = {1: {(2, 3): None}, (2, 3): {}}


           self.failUnless(results == datagraph, 'incorrect result')
                
        def testNodeDel(self): 
 
 	  datagraph = self.datagraph
          datagraph += 1
          datagraph += 2 
          datagraph[2] += 3
          
          datagraph -= 1
    
          results = {2: {3: None}, 3: {}}

          self.failUnless(results == datagraph, 'incorrect result')     
        def testDelRaise(self):

	  datagraph = self.datagraph
          datagraph += 1
          datagraph += 2
          datagraph[2] += 3
          error = 0
	  try:
            for i in range(0,2):
	       datagraph -= 3
          except KeyError:
             error = 1 
 
          self.failUnless(error,'incorrect result')

        def testSetItemRaise(self):
     
           datagraph = self.datagraph
           datagraph += 1
           
           try:
              datagraph[1] = 2
           except ValueError:
              error = 1
          
           self.failUnless(error,'incorrect result')
         
	def testGraphEdges(self): 
           
   	   datagraph = self.datagraph
           graphvals = {1:{2:None},2:{3:None,4:None},5:{2:None},3:{},4:{}}
           edge_list = [[1, 2], [2, 3], [2, 4], [5, 2]]

           for i in graphvals:

             datagraph += i

             for n in graphvals[i].keys():
                datagraph[i] += n
            
           edge_results = []

           for e in datagraph.edges():
              edge_results.append(e)
           
           self.failUnless(edge_results == edge_list, 'incorrect result')        
  
     class IteratorSuite(unittest.TestCase):

        def setUp(self):

           self.datagraph = mapping.dictGraph()
           self.result_kounter = 0 

        def testAttributeIterator(self):

           class dummy_obj(object):
              pass

	   datagraph = self.datagraph
           attr_data = {1: {5:None}, 2: {3:None,1: None}, 3: {}, 5:{}}
           setattr(dummy_obj,'attr_test',attr_data)	    
           querygraph =  { 1:{0:{'attr':'attr_test'}},0:{}} 
           datagraph += dummy_obj
	   datagraph[dummy_obj] += dummy_obj
           result = {0:{0: 1, 1: dummy_obj, (1, 0): {5: None}},1:{0: 2, 1: dummy_obj, (1, 0): {1: None, 3: None}},2:{0: 3, 1: dummy_obj, (1, 0): {}},3:{0: 5, 1:dummy_obj,(1, 0): {}}}
    
           for i in graphquery.GraphQuery(datagraph,querygraph):
               self.failUnless(i == result[self.result_kounter], 'incorrect result')
               self.result_kounter += 1
 
        def testAttrContainerIterator(self):

           class dummy_obj(object):
              pass

	   datagraph = self.datagraph
           attr_data = {1: {5:None}, 2: {3:None,1: None}, 3: {}, 5:{}}
           setattr(dummy_obj,'attr_test',attr_data)
           querygraph =  { 1:{0:{'attrN':'attr_test'}},0:{}}
           datagraph += dummy_obj
           datagraph[dummy_obj] += dummy_obj
           result = {0: {0: 1, 1: dummy_obj},1:{0: 2, 1: dummy_obj},2: {0: 3, 1: dummy_obj},3:{0: 5, 1: dummy_obj}}


           for i in graphquery.GraphQuery(datagraph,querygraph):
               self.failUnless(i == result[self.result_kounter], 'incorrect result')
               self.result_kounter += 1

        def testCallableIterator(self):
            
           def test_method(datanode,datagraph,self):
              for i in datagraph:
                 yield i,datagraph[datanode]

	   datagraph = self.datagraph
           datagraph = {0: {1: None, 2: None, 3: None}, 1: {3: None}, 2: {}, 3: {}}
       
           querygraph = {0: {1: {'f': test_method}, 2: None, 3: None}, 1: {3: None}, 2: {}, 3: {}}

           result = {0: {0: 0, 1: 1, 2: 2, (0, 1): {1: None, 2: None, 3: None}, 3: 3}}
           for i in graphquery.GraphQuery(datagraph,querygraph):
               self.failUnless(i == result[self.result_kounter], 'incorrect result')
      	       self.result_kounter += 1 


        def testCallableContainerIterator(self):

           def test_method(datanode,datagraph,self):
              for i in datagraph:
                 yield i

	   datagraph = self.datagraph
           datagraph = {0: {1: None, 2: None, 3: None}, 1: {3: None}, 2: {}, 3: {}}

           querygraph = {0: {1: {'fN': test_method}, 2: None, 3: None}, 1: {3: None}, 2: {}, 3: {}}

           result = {0: {0: 0, 1: 1, 2: 2, 3: 3}}

           
           for i in graphquery.GraphQuery(datagraph,querygraph):
               self.failUnless(i == result[self.result_kounter], 'incorrect result')
               self.result_kounter += 1


        def testSubQueryIterator(self):
        
           subqueries = []
           subquery = {3: {}, 4: {3: None}}
	   datagraph= self.datagraph
           querygraph = {0:{2:None},1:{2:{'subqueries':subqueries}},2:{},3:{}}
	   datagraph = {0: {1: None, 2: None, 3: None}, 1: {4: None}, 2: {4: None}, 3: {}, 4: {1: None, 3: None}}

           subqueries.append(subquery)

           result =	{0:{0: 0, 1: 1, 2: 2, 3: 3, 4: 4},\
			 1:{0: 0, 1: 1, 2: 3, 3: 4, 4: 2},\
			 2:{0: 0, 1: 2, 2: 3, 3: 1, 4: 4},\
			 3:{0: 0, 1: 2, 2: 1, 3: 3, 4: 4},\
			 4:{0: 0, 1: 2, 2: 3, 3: 4, 4: 1},\
			 5:{0: 0, 1: 3, 2: 2, 3: 1, 4: 4},\
			 6:{0: 0, 1: 3, 2: 1, 3: 4, 4: 2},\
			 7:{0: 0, 1: 3, 2: 2, 3: 4, 4: 1},\
			 8:{0: 1, 1: 2, 2: 4, 3: 3, 4: 0},\
			 9:{0: 1, 1: 3, 2: 4, 3: 2, 4: 0},\
			 10:{0: 2, 1: 1, 2: 4, 3: 3, 4: 0},\
			 11:{0: 2, 1: 3, 2: 4, 3: 1, 4: 0},\
			 12:{0: 4, 1: 1, 2: 3, 3: 2, 4: 0},\
			 13:{0: 4, 1: 2, 2: 3, 3: 1, 4: 0},\
			 14:{0: 4, 1: 2, 2: 1, 3: 3, 4: 0},\
	 		 15:{0: 4, 1: 3, 2: 1, 3: 2, 4: 0}}

           
           for i in graphquery.GraphQuery(datagraph,querygraph):
               self.failUnless(i == result[self.result_kounter], 'incorrect result')
               self.result_kounter += 1
                      
     suite_list =[QuerySuite,MappingSuite,IteratorSuite]

     test_results = []

     for s in suite_list:
        testrun = unittest.makeSuite(s)
        test_results.append(unittest.TextTestRunner(verbosity=2).run(testrun))

     for res in test_results:
        if(res.wasSuccessful()):
           continue
        else:
           return False 
     return True
       
 
if __name__ == "__main__":
  
   TestFrameWork().go()
