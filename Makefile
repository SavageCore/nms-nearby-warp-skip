# Nearby Warp Countdown Skip

# A Nozavolochen mod: skips the Forsaken nearby-system warp hold.
# The host DLL applies mod.toml at game boot.
#
# What it is: two pattern patches, each fail-loud (countdown UI forced to
# zero; wait gate NOPed so the warp engages on the first frame).
#
# Usage:
#   make release      verify spec + pack dist/ zip (default)
#   make verify       verify mod.toml against NMS.exe (read-only)
#   make loader       build the Nozavolochen host DLL via the framework (dev testing)
#   make rootzip      pack the root-install archive into dist/ (no re-verify)
#   make assets       regenerate the Nexus page images (header + gallery)
#   make clean        remove build/ and dist/
#
# Override the framework checkout or game binary if needed:
#   make FRAMEWORK_HOME=/path/to/framework NMS_EXE=/path/to/NMS.exe release

FRAMEWORK_HOME ?= /home/savagecore/Modding/NMS/nozavolochen/framework
NMS_EXE ?= /home/savagecore/.steam/steam/steamapps/common/No Man's Sky/Binaries/NMS.exe

MOD_SET := Nearby Warp Countdown Skip

BUILD := build
DIST := dist

FRAMEWORK_DIST := $(FRAMEWORK_HOME)/loader/dist
DLL := $(FRAMEWORK_DIST)/xinput9_1_0.dll

ROOTZIP := $(DIST)/$(MOD_SET).zip

.PHONY: all release verify loader rootzip assets video clean

all: release

release: verify rootzip
	@echo "release: $(ROOTZIP)"

verify:
	@python3 "$(FRAMEWORK_HOME)/tools/check_specs.py" "$(NMS_EXE)" .
	@echo "verify: OK"

loader:
	@$(MAKE) -C "$(FRAMEWORK_HOME)" loader
	@echo "loader: $(DLL)"

rootzip: verify
	@rm -rf "$(BUILD)/rootzip" && mkdir -p "$(BUILD)/rootzip/$(MOD_SET)"
	@cp mod.toml "$(BUILD)/rootzip/$(MOD_SET)/"
	@mkdir -p "$(DIST)" && rm -f "$(ROOTZIP)" && cd "$(BUILD)/rootzip" && zip -qr "$(shell pwd)/$(ROOTZIP)" "$(MOD_SET)"
	@echo "packed: $(ROOTZIP)"
	@unzip -l "$(ROOTZIP)" | tail -4

assets:
	python3 assets/generate.py

video:
	python3 assets/combine.py

clean:
	rm -rf "$(BUILD)" "$(DIST)"
