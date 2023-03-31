#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 15:08:22 2022

@author: jrdonoso
"""
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm

class Customer:
    
    def __init__(self, _id, curr_state, active = True):
        self._id = _id
        self.curr_state = curr_state
        self.active = active
    def __repr__(self):
        return f'<Customer {self._id} is in {self.curr_state}>'
        
    def next_state(self, P):
        probs = P.to_dict(orient='index')
        for key in probs.keys():
            probs[key] = list(probs[key].values())
        states = list(probs.keys())
        self.curr_state = random.choices(states, weights=probs[self.curr_state])[0]
        
    def is_active(self):
        if self.curr_state=='checkout':
            self.active = False
            return False
        else:
            return True


class Supermarket:
    
    def __init__(self, P, 
                 sections = ['entrance','checkout', 'dairy', 'drinks', 'fruit', 'spices']):
        self.sections = sections
        self.customers = []
        self.transition_matrix = P
        self.section_lim = {'drinks': [120, 220, 200, 450], 
                            'dairy': [350, 450, 200, 450],
                            'spices':[580, 680, 200, 450],
                            'fruit':[810, 910,200,450],
                            'checkout': [100,500,660,740],
                            'entrance': [700,950,660,740]}
        self.layout = plt.imread('market.png')
        self.curr_time = pd.Timestamp('2022-11-18T08')
        self.event_table = []
        
    def update_time(self):
        self.curr_time = self.curr_time + pd.Timedelta(minutes=1)
    
    def add_customer(self, state): #Create new costumer and add it 
        #assert isinstance(customer, Customer)
        if any(self.customers):
            new_id = max([cust._id for cust in self.customers]) + 1
        else:
            new_id = 1
        new_customer = Customer(new_id, state)
        self.customers.append(new_customer)
        self.event_table.extend([[self.curr_time,new_id,'entrance']])
        
    def remove_customer(self,customer_no):
        del self.customers[customer_no]
        
    def init_customers(self, n_customers, init_probs=[]):
        if not any(init_probs):
            init_probs = [1, 0, 0, 0, 0,0]
        for k in range(n_customers):
            self.add_customer(random.choices(self.sections, weights=init_probs)[0])
            
    def update_customers(self):
        self.update_time()
        for k, cust in enumerate(self.customers):
            if cust.is_active():
                cust.next_state(self.transition_matrix)
                self.event_table.extend([[self.curr_time,cust._id,cust.curr_state]])
            else:
                self.customers[k] = np.nan
        while np.nan in self.customers: #Remove nans from customers
            self.customers.remove(np.nan)
            
    def states(self):
        for k, cust in enumerate(self.customers):
            print(f"Customer {cust._id} is on section: {cust.curr_state}")
            
    def display(self):
        plt.imshow(self.layout)
        colors = cm.tab20(np.linspace(0, 1, 20))
        #random.shuffle(colors)
        #x=[]
        #y=[]
        for cust in self.customers:
            xy_lims = self.section_lim[cust.curr_state]
            #x.extend([np.random.uniform(xy_lims[0],xy_lims[1])])
            #y.extend([np.random.uniform(xy_lims[2],xy_lims[3])])
            x = np.random.uniform(xy_lims[0],xy_lims[1])
            y = np.random.uniform(xy_lims[2],xy_lims[3])
            curr_fig = plt.scatter(x, y, color=colors[(cust._id-1) % 20],s=40)
            plt.axis('off')
            plt.title(self.curr_time)
        return curr_fig
        #cust_ids = [cust._id for cust in self.customers]
        #plt.scatter(x, y, c=cust_ids, s=40)
            
    def simulate(self,n_iterations, save_figs = False):
        for k in range(n_iterations):
            self.update_customers()
            self.init_customers(np.random.poisson(lam=2.8))
            curr_fig = self.display()
            if save_figs:
                fig = curr_fig.get_figure()
                fig.savefig(f"./figs/anim_{k}.png") 
                plt.close()
                
    def events_dataframe(self):
        return pd.DataFrame(self.event_table,
                            columns = ['timestamp','customer_no','location'])
         #pd.DataFrame(l1,columns=['timestamp','customer_no','location'])   
# class Simulation(Supermarket):
#     "Child class inheriting from supermarket"
#     def __init__(self,P):
#         Supermarket.__init__(P)
#         self.event_table = []
        
#     def run(self,n_iterations):
#         for iter in range(n_iterations):
#             self.simulate(n_iterations)
    
          
        
        
