```mermaid
C4Context
title Purchase Portal System
Person(admin, "Admin", "Manages vendors and funds")
System(system, "Purchase Portal App", "Web app for ordering and fund allocation")
Rel(admin, system, "Configures rules and reviews vendor invoices")

Person(parent, "Parent/Guardian", "Places student orders")
Person(vendor, "Vendor", "Provides educational products")

System_Ext(azure, "Azure AI Chat Bot", "Answers parent questions")
System_Ext(sendgrid, "SendGrid Email", "Sends order updates")

Rel(parent, system, "Submits order requests")
Rel(system, vendor, "Sends purchase requests")
Rel(system, azure, "Uses chatbot for Q&A")
Rel(system, sendgrid, "Sends emails to parents")

Boundary(school, "School District") {
    System(system)
    Person(teacher, "Teacher")
}

