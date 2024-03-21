from __future__ import annotations
from dataclasses import dataclass 
from docplex.mp.context import *
from docplex.mp.model import Model
from typing import Optional
import numpy as np 
import math
@dataclass()
class LPInstance:
   
    numCustomers : int        		# the number of customers	   
    numFacilities : int           	# the number of facilities
    allocCostCF : np.ndarray   	# allocCostCF[c][f] is the service cost paid each time customer c is served by facility f
    demandC :  np.ndarray   	     		# demandC[c] is the demand of customer c
    openingCostF: np.ndarray   	        # openingCostF[f] is the opening cost of facility f
    capacityF :np.ndarray   	        	# capacityF[f] is the capacity of facility f
    numMaxVehiclePerFacility : int   	 # maximum number of vehicles to use at an open facility 
    truckDistLimit : float        # total driving distance limit for trucks
    truckUsageCost : float		# fixed usage cost paid if a truck is used 
    distanceCF :  np.ndarray   	       # distanceCF[c][f] is the roundtrip distance between customer c and facility f 


   # decision variables: 
      # number of vehicles per facility, array
      # facility open ?
      # map of customer to satisfying facility (array)
   # constraints
   # minimize(openingCost * numFacilitiesOpen + truckUsageCost * sum(numberOfVehiclesFacility) + allocCost[c][f] (iterate through map of customr to satisfying facil))
   # every times a facility shows up in map sum(distanceCF[idx]) < truckDistLimit*numofVehiclesFacility
   # every times a facility shows up in map sum(demand[idx]) < capacityF



def getLPInstance(fileName : str) -> Optional[LPInstance]:
  try:
    with open(fileName,"r") as fl:
      numCustomers,numFacilities = [int(i) for i in fl.readline().split()]
      numMaxVehiclePerFacility = numCustomers 
      print(f"numCustomers: {numCustomers} numFacilities: {numFacilities} numVehicle: {numMaxVehiclePerFacility}")
      allocCostCF = np.zeros((numCustomers,numFacilities))
       

      allocCostraw = [float(i) for i in fl.readline().split()]
      index = 0
      for i in range(numCustomers):
         for j in range(numFacilities):
            allocCostCF[i,j] = allocCostraw[index]
            index+=1
      
      demandC = np.array([float(i) for i in fl.readline().split()])
    
      openingCostF = np.array([float(i) for i in fl.readline().split()])

      capacityF = np.array([float(i) for i in fl.readline().split()])

      truckDistLimit,truckUsageCost = [float(i) for i in fl.readline().split()]
      
      distanceCF =  np.zeros((numCustomers,numFacilities))
      distanceCFraw = [float(i) for i in fl.readline().split()]
      index = 0
      for i in range(numCustomers):
         for j in range(numFacilities):
            distanceCF[i,j] = distanceCFraw[index]
            index+=1
      return LPInstance(
         numCustomers=numCustomers,
         numFacilities=numFacilities,
         allocCostCF=allocCostCF,
         demandC=demandC,
         openingCostF=openingCostF,
         capacityF=capacityF,
         numMaxVehiclePerFacility=numMaxVehiclePerFacility,
         truckDistLimit=truckDistLimit,
         truckUsageCost=truckUsageCost,
         distanceCF=distanceCF
         )


  except Exception as e:
     print(f"Could not read problem instance file due to error: {e}")
     return None 



class LPSolver:
   def __init__(self,filename : str):
      self.lpinst = getLPInstance(filename)
      self.model = Model() #CPLEX solver

   def solve(self):
        # Decision variables
        facilities = range(self.lpinst.numFacilities)
        customers = range(self.lpinst.numCustomers)

        facility_open = self.model.continuous_var_list(facilities, 0, 1, name="facility_open")
        num_vehicles = self.model.continuous_var_list(facilities, 0, self.lpinst.numMaxVehiclePerFacility, name="num_vehicles")
        customer_allocation = self.model.continuous_var_matrix(customers, facilities, 0, 1, name="customer_allocation")


        # Constraints
        for f in facilities:
            # ensure customer demand does not exceed capacity of facility * how open the facility is
            self.model.add_constraint(self.model.sum(customer_allocation[c, f] * self.lpinst.demandC[c] for c in customers) <= self.lpinst.capacityF[f] * facility_open[f])
            # ensure driving distance required by any facility does not exceed max driving distance possible
            self.model.add_constraint(self.model.sum(self.lpinst.distanceCF[c][f] * customer_allocation[c, f] for c in customers) <= self.lpinst.truckDistLimit * num_vehicles[f])
            # ensure number of vehicles used at facility is proportionally less than how open the facility is
            self.model.add_constraint(facility_open[f] >= num_vehicles[f] / self.lpinst.numMaxVehiclePerFacility)


        for c in customers:
            # ensure each customers demand is perfectly met
            # self.model.add_constraint(self.model.sum(customer_allocation[c, f] * self.lpinst.demandC[c] for f in facilities) == self.lpinst.demandC[c])
            # ensure each customer is only serviced by one location
            self.model.add_constraint(self.model.sum(customer_allocation[c, f] for f in facilities) == 1)

        self.model.minimize(
            # opening cost for each facility
            self.model.sum(self.lpinst.openingCostF[f] * facility_open[f] for f in facilities) +
            # paying for each truck at each facility
            self.model.sum(self.lpinst.truckUsageCost * num_vehicles[f] for f in facilities) +
            # paying for trips for each customer
            self.model.sum(self.lpinst.allocCostCF[c][f] * customer_allocation[c, f] for c in customers for f in facilities)
        )

        self.model.solve()
      #   print("maxVehicles:", self.lpinst.numMaxVehiclePerFacility)
      #   print("maxDistance:", self.lpinst.truckDistLimit)
      #   print("distances", self.lpinst.distanceCF)
      #   results = {
      #       "facility_open": [facility_open[f].solution_value for f in facilities],
      #       "num_vehicles": [num_vehicles[f].solution_value for f in facilities],
      #       "customer_allocation": [[customer_allocation[c, f].solution_value for f in facilities] for c in customers],
      #       "total_cost": self.model.objective_value
      #   }
      #   print(results)
        
        return self.model.objective_value
  

def dietProblem():
    # Diet Problem from Lecture Notes
    m = Model()
    # Note that these are continous variables and not integers 
    mvars = m.continuous_var_list(2,0,1000)
    carbs = m.scal_prod(terms=mvars,coefs=[100,250])
    m.add_constraint(carbs >= 500)
    
    m.add_constraint(m.scal_prod(terms=mvars,coefs=[100,50]) >= 250) # Fat
    m.add_constraint(m.scal_prod(terms=mvars,coefs=[150,200]) >= 600) # Protein

    m.minimize(m.scal_prod(terms=mvars,coefs=[25,15]))

    sol  = m.solve()
    obj_value = math.ceil(m.objective_value) 
    if sol:
       m.print_information()
       print(f"Meat: {mvars[0].solution_value}")
       print(f"Bread: {mvars[1].solution_value}")
       print(f"Objective Value: {obj_value}")
    else:
       print("No solution found!")