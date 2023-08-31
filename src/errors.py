def getErrorMessage(error):
    match error:
        case 1:
            return "Provided user is not in the database. Make sure that they have logged at least one patrol."
        case 2:
            return "This user is already a superuser."
        case 3:
            return "This user is already not a superuser."
        case 4:
            return "Already on the first page."
        case 5:
            return "Already on the last page."