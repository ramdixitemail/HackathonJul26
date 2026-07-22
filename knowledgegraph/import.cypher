// =======================================================
// AUDIT KNOWLEDGE GRAPH
// CLEAN IMPORT SCRIPT
// =======================================================


//--------------------------------------------------------
// DELETE EVERYTHING
//--------------------------------------------------------

MATCH (n)
DETACH DELETE n;


//--------------------------------------------------------
// DROP CONSTRAINTS
//--------------------------------------------------------

DROP CONSTRAINT owner_id IF EXISTS;
DROP CONSTRAINT app_id IF EXISTS;
DROP CONSTRAINT server_id IF EXISTS;
DROP CONSTRAINT vuln_id IF EXISTS;
DROP CONSTRAINT audit_id IF EXISTS;


//--------------------------------------------------------
// CREATE CONSTRAINTS
//--------------------------------------------------------

CREATE CONSTRAINT owner_id IF NOT EXISTS
FOR (o:Owner)
REQUIRE o.ownerId IS UNIQUE;

CREATE CONSTRAINT app_id IF NOT EXISTS
FOR (a:Application)
REQUIRE a.appId IS UNIQUE;

CREATE CONSTRAINT server_id IF NOT EXISTS
FOR (s:Server)
REQUIRE s.serverId IS UNIQUE;

CREATE CONSTRAINT vuln_id IF NOT EXISTS
FOR (v:Vulnerability)
REQUIRE v.vulnId IS UNIQUE;

CREATE CONSTRAINT audit_id IF NOT EXISTS
FOR (a:AuditPoint)
REQUIRE a.auditId IS UNIQUE;


//--------------------------------------------------------
// LOAD OWNERS
//--------------------------------------------------------

LOAD CSV WITH HEADERS FROM 'file:///owners.csv' AS row
CREATE (:Owner{
ownerId:row.ownerId,
name:row.name,
email:row.email,
department:row.department
});


//--------------------------------------------------------
// LOAD APPLICATIONS
//--------------------------------------------------------

LOAD CSV WITH HEADERS FROM 'file:///applications.csv' AS row
CREATE (:Application{
appId:row.appId,
name:row.name,
criticality:row.criticality,
status:row.status,
technology:row.technology
});


//--------------------------------------------------------
// LOAD SERVERS
//--------------------------------------------------------

LOAD CSV WITH HEADERS FROM 'file:///servers.csv' AS row
CREATE (:Server{
serverId:row.serverId,
hostname:row.hostname,
os:row.os,
environment:row.environment,
ip:row.ip
});


//--------------------------------------------------------
// LOAD VULNERABILITIES
//--------------------------------------------------------

LOAD CSV WITH HEADERS FROM 'file:///vulnerabilities.csv' AS row
CREATE (:Vulnerability{
vulnId:row.vulnId,
cve:row.cve,
severity:row.severity,
cvss:toFloat(row.cvss),
status:row.status
});


//--------------------------------------------------------
// LOAD AUDIT POINTS
//--------------------------------------------------------

LOAD CSV WITH HEADERS FROM 'file:///audit_points.csv' AS row
CREATE (:AuditPoint{
auditId:row.auditId,
title:row.title,
rating:row.rating,
status:row.status,
recommendation:row.recommendation
});


//--------------------------------------------------------
// APPLICATION -> OWNER
//--------------------------------------------------------

LOAD CSV WITH HEADERS FROM 'file:///application_owner.csv' AS row
MATCH (a:Application {appId:row.appId})
MATCH (o:Owner {ownerId:row.ownerId})
CREATE (a)-[:OWNED_BY]->(o);


//--------------------------------------------------------
// APPLICATION -> SERVER
//--------------------------------------------------------

LOAD CSV WITH HEADERS FROM 'file:///application_server.csv' AS row
MATCH (a:Application {appId:row.appId})
MATCH (s:Server {serverId:row.serverId})
CREATE (a)-[:DEPLOYED_ON]->(s);


//--------------------------------------------------------
// SERVER -> VULNERABILITY
//--------------------------------------------------------

LOAD CSV WITH HEADERS FROM 'file:///server_vulnerability.csv' AS row
MATCH (s:Server {serverId:row.serverId})
MATCH (v:Vulnerability {vulnId:row.vulnId})
CREATE (s)-[:HAS_VULNERABILITY]->(v);


//--------------------------------------------------------
// APPLICATION -> VULNERABILITY
//--------------------------------------------------------

LOAD CSV WITH HEADERS FROM 'file:///application_vulnerability.csv' AS row
MATCH (a:Application {appId:row.appId})
MATCH (v:Vulnerability {vulnId:row.vulnId})
CREATE (a)-[:AFFECTED_BY]->(v);


//--------------------------------------------------------
// AUDIT -> VULNERABILITY
//--------------------------------------------------------

LOAD CSV WITH HEADERS FROM 'file:///audit_vulnerability.csv' AS row
MATCH (a:AuditPoint {auditId:row.auditId})
MATCH (v:Vulnerability {vulnId:row.vulnId})
CREATE (a)-[:IDENTIFIED]->(v);


//--------------------------------------------------------
// AUDIT -> APPLICATION
//--------------------------------------------------------

LOAD CSV WITH HEADERS FROM 'file:///audit_application.csv' AS row
MATCH (a:AuditPoint {auditId:row.auditId})
MATCH (b:Application {appId:row.appId})
CREATE (a)-[:FOR_APPLICATION]->(b);


//--------------------------------------------------------
// SUMMARY
//--------------------------------------------------------

MATCH (n)
RETURN count(n) AS TotalNodes;

MATCH ()-[r]->()
RETURN count(r) AS TotalRelationships;