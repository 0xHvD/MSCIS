import re

TOPIC_MAP = {
    "Active Directory": ["AD ", "Active Directory", "Domain Controller", "Kerberos", "NTLM", "LDAP", "LDAPS"],
    "Tiering Model": ["Tier 0", "T0", "T1", "T2", "Enterprise Access Model"],
    "PAW": ["Privileged Access Workstation", "PAW"],
    "ADCS/PKI": ["AD CS", "PKI", "Certificate", "CBA", "ESC"],
    "Entra ID": ["Microsoft Entra", "Azure AD", "Conditional Access", "Identity Protection", "PIM", "Administrative Unit", "Cross-tenant"],
    "Windows Security": ["Credential Guard", "LSA", "AppLocker", "WDAC", "Sysinternals", "Sysmon", "Windows Baseline"],
    "Hybrid Identity": ["Entra Connect", "Cloud Sync", "PTA", "Seamless SSO", "Kerberos in the cloud"],
}

def classify(text):
    hits = set()
    for topic, keywords in TOPIC_MAP.items():
        for k in keywords:
            if re.search(rf"\b{re.escape(k)}\b", text, flags=re.I):
                hits.add(topic)
                break
    return sorted(hits)

if __name__ == "__main__":
    import sys, json
    txt = " ".join(sys.argv[1:]) or "New Conditional Access soft delete and restore in Entra ID"
    print(json.dumps({"topics": classify(txt)}, indent=2))
