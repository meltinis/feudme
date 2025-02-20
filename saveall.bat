# Prompt the user for a commit message.
$commitMessage = Read-Host "Enter your commit message"

Write-Output "Staging changes..."
git add .

Write-Output "Creating commit..."
git commit -m $commitMessage

Write-Output "Pushing to remote..."
git push
