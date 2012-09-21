# Calculate Ideal Points of Legislators
library("RSQLite")
library("pscl")
library("ggplot2")

# Load Data 
# Path to SQLite Database #
conn <- dbConnect("SQLite", dbname = "/home/christopher/Dropbox/CongressMonitor/StateGovTracker.db")

# Get Votes Table
votes <- dbReadTable(conn, "pa_legis_votes")
vote_sub <- votes[,1:3]

# Get Member Table
mem_info <- dbReadTable(conn, "officials")
party_data <- cbind(mem_info$legid, mem_info$party)

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

# Combine Ideal Points with Party Data #
ideal_scores <- cbind(votes_wide[,1], id1$xbar)
ideal_scores <- data.frame(ideal_scores, row.names=NULL)
party_df <- data.frame(party_data)
combined <- merge(party_df, ideal_scores, by.x = "X1", by.y = "V1")
parties <- combined$X2

qplot(combined$D1, ..density.., data=combined, geom="density", fill="#FF6666", colour = "black", title="Aggregate")

