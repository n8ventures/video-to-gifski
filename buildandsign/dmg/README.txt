If you encounter anything like:
"N8's Video To GIF Converter (Beta).app is damaged and can’t be opened"
"N8's Video To GIF Converter (Beta).app cannot be opened because the developer cannot be verified"
'"N8's Video To GIF Converter (Beta)" can't be opened because Apple cannot check it for malicious software."

Just copy this code, and then paste and run this on your Terminal:
sudo xattr -dr com.apple.quarantine "/Applications/N8's Video To GIF Converter (Beta).app"

OR

Go to your /Applications folder, then right-click the app and press 'Open', a pop-up will appear, then click 'Open' again.
More info here: https://support.apple.com/en-ph/guide/mac-help/mchleab3a043/mac