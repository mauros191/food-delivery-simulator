# Online Food Delivery Company Problem (OFDCP)

Starting from the Meal Delivery Routing Problem, a formalization of the food delivery problem proposed by Reyes et al., the problem it was reformalaized by adding some features (e.g. new algorithms to batch the orders, possibility for the rider to reject an order, introduction of the queue) and it was built from scratch a dedicate discrete-event simulator using Python 3.10. It was used OSRM mounted via Docker to calculate the shortest path on the street network and Google OR-Tools to solve the optimization problems. 

Requirements: Python 3.10

<img src="https://raw.githubusercontent.com/maurosaladino/food-delivery-simulator/main/public/demo.gif">
