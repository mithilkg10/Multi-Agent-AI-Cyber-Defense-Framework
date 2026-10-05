const scenarios={
scan:{xgb:.72,cnn:.81,dqn:.75,final:.76,decision:"Elevated reconnaissance pattern. Threshold crossed for controlled deception review."},
brute:{xgb:.89,cnn:.86,dqn:1,final:.90,decision:"Credential-access pattern strongly exceeds the configured threshold."},
ddos:{xgb:.93,cnn:.91,dqn:1,final:.93,decision:"High-confidence traffic anomaly. Response path is eligible for controlled activation."},
sql:{xgb:.82,cnn:.77,dqn:.75,final:.79,decision:"Application-layer attack pattern exceeds the current decision threshold."}
};
const set=(k)=>{const s=scenarios[k];["xgb","cnn","dqn"].forEach(id=>{document.getElementById(id).style.width=(s[id]*100)+"%";document.getElementById(id+"v").textContent=s[id].toFixed(2)});document.getElementById("final").textContent=s.final.toFixed(2);document.getElementById("decision").textContent=s.decision};
document.querySelectorAll(".scenario").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll(".scenario").forEach(x=>x.classList.remove("active"));b.classList.add("active");set(b.dataset.scenario)}));set("scan");