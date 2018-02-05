PI ?= raspberrypi3.local

SHORTCUTS = $(wildcard shortcuts/*.desktop)


deploy_local:
	git ls-files google-assistant-sdk/googlesamples/assistant/library/ | rsync -avz --exclude=".*" --exclude="*.desktop" --files-from - . pi@$(PI):~/gassist/assistant-sdk-python

deploy: deploy_local
