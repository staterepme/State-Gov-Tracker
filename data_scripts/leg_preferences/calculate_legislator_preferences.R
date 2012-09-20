# Calculate Ideal Points of Legislators

# Load Data 
library("RSQLite")
library("pscl")

# Path to SQLite Database #
conn <- dbConnect("SQLite", dbname = "/home/christopher/Dropbox/CongressMonitor/StateGovTracker.db")

# Get Votes Table
votes <- dbReadTable(conn, "pa_legis_votes")
vote_sub <- votes[,1:3]

# Reshape Votes so that each row is a legislator and column is a vote
votes_wide <- reshape(vote_sub, idvar="legid", timevar="bill_id", direction="wide")

# Create Roll Call Vote Object #
colnames(votes_wide)[1] <- "legis.names"
length(colnames(votes_wide))
vote_wide_sub <- votes_wide[,2:699]
rc <- rollcall(vote_wide_sub, legis.names=votes_wide[,1])

# Calculate Ideal Points #
id1 <- ideal(rc,
             d=1,
             startvals="eigen",
             normalize=TRUE,
             store.item=TRUE,
             maxiter=10000,
             burnin=1000,
             thin=100,
             verbose=TRUE)  

summary(id1)