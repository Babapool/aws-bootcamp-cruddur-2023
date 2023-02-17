# Week 0 — Billing and Architecture

## Overview

During this week's live stream, we discussed about AWS billing, AWS architecture and AWS security. We also talked about the app (Cruddur) we are going to build. We also talked about the various different personas of the stakeholders involved in the making of this app.

We also leaned about the Iron Triangle which has 3 vertices to determine the Quality of your project. The three vertices are:
- Scope (Features, functionality)
- Cost (Budgets, Resources)
- Time (Schedule)

So if we want something quick and scope the scope of the project will be limited. This triangle tells about the various tradeoffs that one may occur while managing a project.

In the next part we learned about **"What is Good Architecture?"**:
- The project **Must** achieve some requirements which can either be technical or business oriented.
- Those requirements must be:
  - Verifiable
  - Monitorable
  - Traceable
  - Feasible
- It should address the _Risks_,_Assumptions_ and _Constraints_ of the project.

All in all this in the end in some ways ties in with the concept of the Iron Triangle.

Then we learnt about the diffent types of designs:
1. Conceptual Design: Business requirements/Concept translated into ways that can be understand by non techincal people whichh includes the way the product will function.
1. Logical Design: This is a zommed in version of the Conceptual design. It defines how the system should be implemented, included the enviroments and services to be used. It is the blueprint of the product.
1. Physical Design: It is actual represented on the product that is going to be bulit, which will be understood by the technical working on it.

Finally we learned about the __AWS Well-Architected Framework__. The AWS Well-Architected Framework is a set of practice which you can use to review your AWS workloads againsts standard AWS best practices.

It has 6 operational pillars:
- Operational Excellence
- Security
- Reliability
- Performance Efficiency
- Cost Optimization
- Sustainability

You can learn more about these 6 pillars from [here](https://aws.amazon.com/architecture/well-architected/?wa-lens-whitepapers.sort-by=item.additionalFields.sortDate&wa-lens-whitepapers.sort-order=desc&wa-guidance-whitepapers.sort-by=item.additionalFields.sortDate&wa-guidance-whitepapers.sort-order=desc).

## Required Homework

### Conceptual Diagram of Cruddur
![Conceptual Diagram of Cruddur]()

You can view this diagram in Lucid Chart from [here](https://lucid.app/lucidchart/4224de5d-2627-429f-8534-e0a8419c20ec/edit?viewport_loc=-183%2C98%2C2075%2C947%2C0_0&invitationId=inv_be31f293-d9f6-462b-9313-3e15324159f8).

### Logical Diagram of Cruddur
![Logical Diagram of Cruddur](assets/Logical-Diagram-Cruddur.svg)

You can view this diagram in Lucid Chart from [here](https://lucid.app/lucidchart/48948c93-30b3-408e-8e0b-1795cba9a759/edit?viewport_loc=-903%2C929%2C2379%2C1085%2C0_0&invitationId=inv_04005c7d-b935-406d-b11d-9c11a511a4e6).

