SHELL=/usr/bin/env sh

source_c_to_obj=$(addprefix $(2)/,$(patsubst %.c,%.o,$(notdir $(1))))
source_c_to_exe=$(addprefix $(2)/,$(patsubst %.c,%.exe,$(notdir $(1))))

project_TAG:=gotoglobe
project_DIR:=$(CURDIR)

target_TAG:=debian-8.3

tmp_DIR:=build/$(target_TAG)/tmp
lib_DIR:=build/$(target_TAG)/lib
bin_DIR:=build/$(target_TAG)/bin
log_DIR:=log

CC:=gcc
CFLAGS:=-std=c99 -pedantic -Wall -Wno-missing-braces -Winline \
	-g -fPIC -fno-strict-aliasing -O2 -I include 

src_DIR:=./src
src_LST:=$(wildcard $(src_DIR)/*.c)
src_OBJ:=$(call source_c_to_obj,$(src_LST),$(tmp_DIR))

test_DIR:=./test
test_LST:=$(wildcard $(test_DIR)/*.c)
test_EXE:=$(call source_c_to_exe,$(test_LST),$(bin_DIR))

dynamic_LIB:=$(lib_DIR)/lib$(project_TAG).so
static_LIB:=$(lib_DIR)/lib$(project_TAG).a

.PHONY: preface postface create_dir clean test all

all: preface $(dynamic_LIB) $(static_LIB) postface
test: all $(test_EXE)

$(tmp_DIR)/%.o:$(src_DIR)/%.c
	@echo "compile. $(notdir $@)"
	@$(CC) -c $(CFLAGS) $< -o $@

$(bin_DIR)/%.exe:$(test_DIR)/%.c
	@echo "test. $(notdir $@)"
	@$(CC) -L $(lib_DIR) -lm -lgotoglobe $(CFLAGS) $< -o $@
	@LD_LIBRARY_PATH=$(lib_DIR) $@ | tee $(log_DIR)/$(notdir $(basename $@)).log

$(dynamic_LIB): $(src_OBJ)
	@echo "link. $(notdir $@)"
	@$(CC) $(CFLAGS) -shared -o $@ -Wl,--whole-archive $^ -Wl,--no-whole-archive

$(static_LIB): $(src_OBJ)
	@echo "archive. $(notdir $@)"
	@ar rsu $@ $?

preface: create_dir
	@echo "\n>>>  BUILD  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  $(project_DATE)  >>>\n"
	@echo "\tproject: $(project_TAG)\n"
	@echo "\ttarget: $(target_TAG)"
	@echo "\n=====================================================================\n"

postface:
	@echo "\n=====================================================================\n"
	@echo "products:"
	@echo "\t$(dynamic_LIB)"
	@echo "\t$(static_LIB)"
	@echo "\n<<<  $(target_TAG)  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  END  <<<\n"

create_dir:
	@mkdir --parents $(tmp_DIR)
	@mkdir --parents $(lib_DIR)
	@mkdir --parents $(bin_DIR)
	@mkdir --parents $(log_DIR)

clean:
	-@rm --recursive --force $(tmp_DIR)
	-@rm $(dynamic_LIB)
	-@rm $(static_LIB)
	-@rm $(bin_DIR)/*.exe
	@echo "\ncleaned ... \n"
