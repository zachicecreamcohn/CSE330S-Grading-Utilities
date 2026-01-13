| Earned | Possible | Requirement                                                                                                   | Feedback |
| ------ | -------- | ------------------------------------------------------------------------------------------------------------- | -------- |
| 0      | 4        | Users should not be able to see any files until they log in, users.txt should not be accessible to the public |          | <!-- -2pts if users.txt is served by apache -->
| 0      | 4        | User can see a list of uploaded files                                                                         |          | <!-- -2pts if you can still see deleted files, -1pt if you can see "files" like "." and ".." -->
| 0      | 5        | Users can open uploaded files                                                                                 |          | <!-- -4pts if user cannot open images or other binary files (eg docx), -2pts if downloads as .php, -5pts if cannot upload images-->
| 0      | 4        | Users can upload files, files are stored securely                                                             |          | <!-- -2pts if files are served by apache-->
| 0      | 4        | Users can delete files                                                                                        |          | <!-- needs to be actually deleted from the filesystem -->
| 0      | 2        | Directory structure is not exposed                                                                            |          | <!-- also means not passing absolute paths like "/srv/uploads/foo.txt" -->
| 0      | 2        | User can log out                                                                                              |          | <!-- -1 point if sessions are used but not destroyed -->
| 0      | 4        | Code is well formatted and easy to read                                                                       |          |
| 0      | 3        | Site follows FIEO                                                                                             |          | <!-- -1.5pts if any filename or username isn't properly filtered, -1.5pts if any user-controlled text isn't properly escaped -->
| 0      | 3        | All pages pass the W3C validator                                                                              |          | <!-- 0pts if any errors, -1 point per warning -->
| 0      | 5        | AI reflection                                                                                                 |          | <!-- -4pts if no written reflection in README.md, -1pt if nothing in AI interaction log (CSE3300_AI_LOG.md) -->
| 0      | 4        | Site is intuitive to use and navigate                                                                         |          | <!-- -2pts for each of the following: manually pressing browser back button (except viewing uploaded files), needing to do a hard refresh to make things work properly, needing to manually modify the URL -->
| 0      | 1        | Site is aesthetically pleasing                                                                                |          |

## Creative Portion (10 possible)

| Earned | Feature | Feedback |
| ------ | ------- | -------- |
|        |         |          |

## Grade

| Total Earned | Total Possible |
| ------------ | -------------- |
| 0            | 55             |
