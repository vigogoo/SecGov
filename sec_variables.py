# items
items = {
  "10-K":{
"1":"Financial Statements",
"1A":"Risk Factors",
"1B":"Unresolved Staff Comments",
"2":"Properties",
"3":"Legal Proceedings",
"4":"Mine Safety Disclosures",
"5":"Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities",
"6":"Selected Financial Data",
"7":"Discussion and Analysis of Financial Condition and Results of Operations",
"7A":"Quantitative and Qualitative Disclosures about Market Risk",
"8":"Financial Statements and Supplementary Data",
"9":"Changes in and Disagreements with Accountants on Accounting and Financial Disclosure",
"9A":"Controls and Procedures",
"9B":"Other Information",
"10":"Directors, Executive Officers and Corporate Governance",
"11":"Executive Compensation",
"12":"Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters",
"13":"Certain Relationships and Related Transactions, and Director Independence",
"14":"Principal Accountant Fees and Services"
  },
  "10-Q":{
   "part1":{
"1":"Financial Statements",
"2":"Discussion and Analysis of Financial Condition and Results of Operations",
"3":"Quantitative and Qualitative Disclosures About Market Risk",
"4":"Controls and Procedures"
   },
    "part2":{
"1":"Legal Proceedings",
"1A":"Risk Factors",
"2":"Unregistered Sales of Equity Securities and Use of Proceeds",
"3":"Defaults Upon Senior Securities",
"4":"Mine Safety Disclosures",
"5": "Other Information",
"6": "Exhibits",
}
  }
}  
    
items_10_K = items["10-K"]
items_10_Q_part_I = items["10-Q"]["part1"]
items_10_Q_part_II = items["10-Q"]["part2"]

# tags and keywords to be used to get data in a section
search_items = {
  "10-K":{
"1":["Financial Statements"],
"1A":["Risk Factors"],
"1B":["Unresolved Staff Comments"],
"2":["Properties"],
"3":["Legal Proceedings"],
"4":["Mine Safety Disclosures"],
"5":["Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities"],
"6":["Selected Financial Data"],
"7":["Discussion and Analysis of Financial Condition and Results of Operations"],
"7A":["Quantitative and Qualitative Disclosures about Market Risk"],
"8":["Financial Statements and Supplementary Data"],
"9":["Changes in and Disagreements with Accountants on Accounting and Financial Disclosure"],
"9A":["Controls and Procedures"],
"9B":["Other Information"],
"10":["Directors, Executive Officers and Corporate Governance"],
"11":["Executive Compensation"],
"12":["Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters"],
"13":["Certain Relationships and Related Transactions, and Director Independence"],
"14":["Principal Accountant Fees and Services"]
  },
  "10-Q":{
   "part1":{
"1":["Financial Statements"],
"2":["Discussion and Analysis of Financial Condition and Results of Operations"],
"3":["Quantitative and Qualitative Disclosures About Market Risk"],
"4":["Controls and Procedures"]
   },
    "part2":{
"1":["Legal Proceedings"],
"1A":["Risk Factors"],
"2":["Unregistered Sales of Equity Securities and Use of Proceeds"],
"3":["Defaults Upon Senior Securities"],
"4":["Mine Safety Disclosures"],
"5": ["Other Information"],
"6":[ "Exhibits"],
}
  }
} 