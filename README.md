# OptiMeet ( Traveling Salesman Problem )

OptiMeet is an algorithm for finding the best time for a salesman to visit a client.
The OptiMeet acts as a scheduling recommendation algorithm for a sales team.

## Roles

- Sales Person: The person who is selling the product.
- Client: The person who is buying the product.
- Agent: The person who is scheduling the meetings.

## How it works

The agent will call the client to schedule a time for the sales person to visit the client at his house.
The agent will use the OptiMeet algorithm to find the best time for the sales person to visit the client.
The sales person will use the OptiMeet Mobile App to navigate to the client's house.

## Algorithm Approach

The scheduling optimization uses a hybrid approach combining:

1. **1+1 Evolutionary Strategy**: For optimizing time slots while considering:
   - Sales person's existing schedule
   - Travel time between locations
   - Client availability windows

2. **Constraints Handling**:
   - Hard Constraints:
     - No overlapping meetings
     - Travel time feasibility
     - Working hours compliance
   - Soft Constraints:
     - Minimizing travel distance
     - Preferred meeting times
     - Optimal route planning

3. **Optimization Phases**:
   - Initial scheduling with hard constraints
   - Route optimization using TSP principles
   - Fine-tuning based on soft constraints
   - Final schedule generation

The algorithm aims to minimize travel time while maximizing the number of successful client visits per day.
