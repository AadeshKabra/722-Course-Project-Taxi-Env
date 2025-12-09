The objective of the project is to evaluate the performance of Hierarchical and Classical planning and acting strategies in the Taxi-v3 environment. The project will compare HTN Run-Lookahead and HTN Run-Lazy-Lookahead acting strategies using GTPyhop and Classical Planning approach.

The project would address the following research questions:
- Does hierarchical task decomposition provide computational advantage over classical planning?
- How does the choice of acting strategy affect planning efficiency?
- Which factors enable planning to scale effectively as grid size increases?

Important Files:

- taxi_domain.pddl : It is the Domain file for the Classical Planning approach.
- classical_planning_executor.py : It is the main execution file for the Classical Planning approach.
- htn_executor.py : It is the execution file for the GTPyhop planning approach.
- pyperplan_wrapper.py : Wrapper file for Classical Planning approach.
- gtpyhop_wrapper.py : Wrapper file for GTPyhop.
- visualization.py : Separate Python file for creating charts and visualizations.
- acting_strategies.py : Helper file for acting strategies of Classical Planning.
- htn_acting_strategies: Helper file for acting stratgeies of GTPyhop planning approach.
