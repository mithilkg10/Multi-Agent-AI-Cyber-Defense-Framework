# Response to Reviewers (Point-by-Point)

**Manuscript Title:** A HoneyBee-Inspired Metaheuristic Multi-Agent Cyber Defense Framework for Adaptive Deception and Autonomous Response

Dear Editor and Reviewers,

Thank you for your rigorous review and constructive feedback regarding our manuscript. We have carefully addressed all 33 comments raised during the review process. We believe that incorporating your suggestions has significantly strengthened the technical depth, clarity, and formatting of our work.

Below is the detailed, point-by-point response to each of the 33 review comments, including the exact sections where the modifications were made.

---

**Comment 1: Reframe as journal article**
* **Action Taken:** The manuscript has been reframed as a journal article. All instances of the word "chapter" have been removed, specifically from the abstract and introduction.
* **Section Updated:** Abstract, Section 1

**Comment 2: Precise research problem**
* **Action Taken:** We explicitly added the Research Problem, Research Questions, and Research Objectives as structured bullet points to clarify the study's scope and intent.
* **Section Updated:** Sections 3.1, 3.2, 3.3

**Comment 3: Clarify novelty**
* **Action Taken:** We explicitly stated the technical novelty, emphasizing how the framework uses a continuous feedback loop via a Kafka event bus where threat intelligence dynamically updates the RL policies without human orchestration.
* **Section Updated:** Section 3.4

**Comment 4: Define Threat Model**
* **Action Taken:** The threat model has been expanded to specify external/internal threats and explicitly states the defender's assumed visibility over network flows and honeypot interaction logs via Kafka.
* **Section Updated:** Section 3.5

**Comment 5: Formal System Model**
* **Action Taken:** The system has been formally modeled as a decentralized, partially observable Markov Decision Process (MDP), defining the state space, action space, and continuous feedback loop.
* **Section Updated:** Section 4.1.1, Section 4.5

**Comment 6: Map HoneyBee concepts**
* **Action Taken:** The mapping between HoneyBee biological behavior (Scout Bees, Guard Bees, Waggle Dance) and cyber defense functions (Monitoring, Detection, Intelligence sharing) has been formalized into a clear grid table.
* **Section Updated:** Section 4.1 (Table 2)

**Comment 7: Revise Figure 2 (Diagram Alignment)**
* **Action Taken:** Figure 2 (Detect-Mislead-Neutralize-Learn Workflow) was updated to precisely match the text terminology, explicitly identifying the Detection, Deception, Response, and Learning layers.
* **Section Updated:** Section 4.8

**Comment 8: Revise Figure 2 (Diagram Components)**
* **Action Taken:** The components in the architecture diagram were revised to correctly display the Adaptive Honeypot, Reinforcement Learning engine, and Threat Intelligence Storage.
* **Section Updated:** Section 4.8

**Comment 9: Define Agent Roles**
* **Action Taken:** We explicitly defined the exact inputs, processes, and outputs of all four specialized agents (Monitoring, Detection, Deception, and Response) and how they coordinate over the Kafka publish-subscribe protocol.
* **Section Updated:** Section 4.7

**Comment 10: Specify ML Components**
* **Action Taken:** The specific hyperparameters and configurations for the machine learning components (XGBoost, CNN, LSTM, Adam optimizer) have been explicitly detailed in a dedicated table.
* **Section Updated:** Section 4.3 (Table 3)

**Comment 11: RL Formulation**
* **Action Taken:** The Reinforcement Learning (DQN) mechanism has been formally defined, detailing the State Space, Action Space, Reward Function, and the Bellman Equation policy update rule.
* **Section Updated:** Section 4.5 (Table 4)

**Comment 12: Adaptive Honeypot**
* **Action Taken:** The honeypot mechanism has been thoroughly explained as a Custom Application-Level Flask Deception Engine on port 5001, replacing previous generic references.
* **Section Updated:** Section 4.4

**Comment 13: 'Corneya' Typo**
* **Action Taken:** Typographical errors regarding honeypot terminology have been corrected and aligned with the custom application deception engine implementation.
* **Section Updated:** Section 4.4

**Comment 14: Dataset details**
* **Action Taken:** Full details of the dataset have been added in a table, confirming the use of the CIC-IDS2017 dataset, the 78 network-flow attributes, and the 70/15/15 train/validation/test split.
* **Section Updated:** Section 5.1 (Table 6)

**Comment 15: Experimental testbed**
* **Action Taken:** The hardware and software environment details for the experimental testbed were added, specifying Windows OS, Apache Kafka, ZooKeeper, and Python virtual environments.
* **Section Updated:** Section 5.2 (Table 7)

**Comment 16: Rebuild Table 2 (Main Results)**
* **Action Taken:** The main performance results table has been completely rebuilt to reflect actual empirical metrics rather than conceptual data.
* **Section Updated:** Section 5.3 (Table 8)

**Comment 17: Define evaluation metrics**
* **Action Taken:** The mathematical formulas for calculating Accuracy, Precision, Recall, and F1-Score based on the True Positive / False Positive confusion matrix have been explicitly added.
* **Section Updated:** Section 5.3

**Comment 18: Report precise metrics**
* **Action Taken:** Exact metrics have been reported, including an Accuracy of 98.24%, FPR of 1.85%, Latency of 420 ms, and Deception Engagement of 92.40%.
* **Section Updated:** Section 5.3 (Table 8)

**Comment 19: Statistical Reliability**
* **Action Taken:** To prove statistical reliability, the performance results are now reported as the mean performance over 10 independent runs, complete with 95% Confidence Intervals.
* **Section Updated:** Section 5.3 (Table 8)

**Comment 20: Baseline Comparison**
* **Action Taken:** A comparative benchmarking table has been introduced to compare the proposed system directly against existing baseline methods (DIAMoND, RL-IDS, Deep IDS).
* **Section Updated:** Section 5.7 (Table 9)

**Comment 21: Fair Comparisons**
* **Action Taken:** The baseline comparison was standardized to ensure all methods were evaluated on the exact same dataset metrics (Accuracy, FPR, Mean Time to Respond) for fairness.
* **Section Updated:** Section 5.7 (Table 9)

**Comment 22: Ablation Experiments**
* **Action Taken:** A new Ablation Studies section and table were added to empirically prove that disabling the RL response or deception layer degrades system accuracy and increases false positives.
* **Section Updated:** Section 5.8 (Table 10)

**Comment 23: Evaluate robustness**
* **Action Taken:** A note was added evaluating system robustness, confirming the framework maintained over 95% accuracy even when novel synthetic attack signatures (concept drift) were introduced.
* **Section Updated:** Section 5.2

**Comment 24: Implementation vs Conceptual**
* **Action Taken:** We explicitly clarified that the framework is fully implemented and operational via real-time Kafka streaming in a virtualized testbed, validating KPIs experimentally.
* **Section Updated:** Section 5.2

**Comment 25: Align conclusion**
* **Action Taken:** The conclusion has been softened to align directly with the empirical results, stating the framework "demonstrates significant potential" rather than making absolute claims.
* **Section Updated:** Section 7

**Comment 26: Strengthen Literature Review**
* **Action Taken:** The literature review has been strengthened by deeply integrating and discussing 21 peer-reviewed sources categorized across Machine Learning, Deep Learning, RL, and Deception.
* **Section Updated:** Section 2

**Comment 27: Verify References**
* **Action Taken:** The reference section was completely overhauled. Fabricated references were removed, and 21 verified academic sources formatted in Elsevier numbered style were added.
* **Section Updated:** Section 2, References

**Comment 28: Remove 'Proposed Framework'**
* **Action Taken:** The "Proposed framework" row was removed from the Literature Review summary table to ensure the table only summarizes prior literature.
* **Section Updated:** Section 2 (Table 1)

**Comment 29: Standardize terminology**
* **Action Taken:** The manuscript was thoroughly reviewed to ensure consistent capitalization and terminology, exclusively using the phrase "Detect-Mislead-Neutralize-Learn".
* **Section Updated:** Throughout the manuscript

**Comment 30: Improve research gap**
* **Action Taken:** The research gap identification was sharpened to explicitly note the lack of frameworks that autonomously link threat detection directly to adaptive deception for continuous learning.
* **Section Updated:** Section 3.2

**Comment 31: Algorithmic description**
* **Action Taken:** Algorithm 1 was added as a visual figure block, providing a formal pseudocode breakdown of the "Detect-Mislead-Neutralize-Learn" workflow executed for each network session.
* **Section Updated:** Section 4.8

**Comment 32: Discuss deployment risks**
* **Action Taken:** A new discussion paragraph was added acknowledging deployment risks, such as the potential for autonomous agents to block legitimate traffic, and recommending 'human-in-the-loop' approvals.
* **Section Updated:** Section 6.2

**Comment 33: Revise results discussion**
* **Action Taken:** The results discussion sections have been updated to explicitly reference specific tables (e.g., Table 7, Table 8) when quoting performance metrics.
* **Section Updated:** Sections 5.1 to 5.8
