# Response to Reviewers

**Manuscript Title:** A HoneyBee-Inspired Metaheuristic Multi-Agent Cyber Defense Framework for Adaptive Deception and Autonomous Response
**Authors:** Shaista Tarannuma, Dr. Jyothi A P, Mithil K Gowda, GR Dikshith, Chandana B S, Pranathi M

Dear Editor and Reviewers,

Thank you for your rigorous review and constructive feedback regarding our manuscript. We have carefully addressed all 33 comments raised during the review process. We believe that incorporating your suggestions has significantly strengthened the technical depth, clarity, and formatting of our work, ensuring it fully meets the high standards of the journal.

Below is a detailed, point-by-point summary of the revisions made in the updated manuscript.

---

### Part 1: Structural and Formatting Revisions
| Reviewer Comment | Authors' Response & Action Taken |
| :--- | :--- |
| **[1] Reframe as journal article** | We have removed all instances of the word "chapter" throughout the manuscript, specifically in the abstract and introduction, to align with the journal article format. |
| **[27] Verify References** | We completely overhauled the reference section. We replaced 20 prior references with 21 verified, peer-reviewed academic sources formatted strictly in Elsevier numbered style. |
| **[6, 31] Formatting In-text citations** | All 21 references have been actively cited in the text using bracketed numbers (e.g., [1], [2]) within Sections 1 and 2 to ensure no references are left orphaned. |
| **[33] Table numbering and captions** | Table numbering has been fixed sequentially from Table 1 to Table 10. All captions have been moved to the bottom of the tables and formatted correctly using periods (e.g., "Table 1. Literature Review."). |
| **[12] Abstract formatting** | The abstract has been merged into a single, continuous paragraph to strictly comply with the journal's formatting guidelines. |
| **[29] Standardize terminology** | We performed a thorough review to ensure consistent use of the "Detect-Mislead-Neutralize-Learn" workflow and capitalized "HoneyBee Method" uniformly. |

### Part 2: Technical and Architectural Clarifications
| Reviewer Comment | Authors' Response & Action Taken |
| :--- | :--- |
| **[2] Precise research problem** | Explicit Research Questions and Objectives were added as bullet points in Section 3.1 and 3.2 to clearly frame the scope of the study. |
| **[3] Clarify novelty** | Section 3.4 was updated to explicitly state: "Unlike existing moving-target defenses that rely on static rules, the HoneyBee Method introduces a continuous feedback loop where threat intelligence gathered by deception agents dynamically updates the reinforcement learning response policies in real-time." |
| **[4] Define Threat Model** | Section 3.5 was expanded to explicitly state the assumed defender visibility, noting that defenders have full visibility over network flows and honeypot interaction logs via Kafka. |
| **[5, 11] RL Formulation** | Section 4.5 was entirely rewritten to formally define the autonomous response as a Markov Decision Process (MDP). We explicitly defined the State Space (S), Action Space (A), Reward Function (R), and the Bellman Equation policy update rule. |
| **[12, 13] Adaptive Honeypot** | We updated Section 4.4 to detail our Custom Application-Level Flask Deception Engine on port 5001, replacing generic references to Cowrie and explaining the deterministic column-wise derangement algorithm used. |
| **[9] Define Agent Roles** | Section 4.7 was revised to explicitly define the inputs and outputs of all four agents (Monitoring, Detection, Deception, and Response), detailing their communication over the Apache Kafka bus. |
| **[10] Specify ML Components** | We added Table 3 (Detection Model Configurations) in Section 4.3, specifying the use of XGBoost (Stage 1) and CNN-LSTM (Stage 2) architectures, including hyperparameters like learning rates and layer counts. |
| **[31] Algorithmic description** | We added Algorithm 1, detailing the exact pseudocode for the "Detect-Mislead-Neutralize-Learn" workflow, placed just before Section 4.9. |

### Part 3: Experimental Results and Evaluation
| Reviewer Comment | Authors' Response & Action Taken |
| :--- | :--- |
| **[14] Dataset details** | Added Table 6 in Section 5.1 detailing the CIC-IDS2017 dataset, the 78 network-flow attributes used, and the 70/15/15 data split. |
| **[15] Experimental testbed** | Added Table 7 in Section 5.1 specifying the testbed runs on Windows OS, utilizing Apache Kafka, ZooKeeper, and Python virtual environments for the models. |
| **[17] Define evaluation metrics** | Added mathematical definitions for Accuracy, Precision, Recall, and F1-Score in Section 5.3 based on the True Positive / False Positive confusion matrix. |
| **[16, 18, 19] Report precise metrics** | Replaced the old performance table with Table 8, reporting exact mean metrics over 10 runs with 95% confidence intervals (Accuracy 98.24% ± 0.15%, FPR 1.85% ± 0.20%, Latency 420 ms ± 45 ms). |
| **[20, 21] Baseline Comparison** | Added Table 9 to compare the proposed system directly against DIAMoND, RL-IDS Baseline, and Deep IDS Baseline, proving superior accuracy and lower latency. |
| **[22] Ablation Experiments** | Added a new "Section 5.8 Ablation Studies" alongside Table 10. This proves empirically that disabling the RL response or deception layer degrades accuracy to 96.12% and 95.35% respectively. |
| **[23, 24] Evaluate robustness** | Clarified in Section 5.2 that the framework is fully implemented via real-time Kafka streaming (not just conceptual) and maintains >95% accuracy against novel synthetic attack signatures. |
| **[32] Discuss deployment risks** | Added a paragraph to Section 6.2 acknowledging the risk of autonomous agents blocking legitimate traffic and recommending 'human-in-the-loop' approvals for high-impact actions, alongside privacy compliance for honeypot payloads. |
| **[25] Align conclusion** | Softened the claims in Section 7 to state the framework "demonstrates significant potential for closed-loop self-improvement based on empirical testbed results," avoiding overclaiming. |

We are grateful to the reviewers for pushing us to refine the manuscript to this level of rigor. We look forward to your final decision.

Sincerely,
The Authors
