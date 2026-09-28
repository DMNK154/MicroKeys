cmake_minimum_required(VERSION 3.22)

project(MicroKeys VERSION 0.2.1)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Link the MSVC runtime statically so the plugin and app run on PCs without the
# Visual C++ Redistributable installed.
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

add_subdirectory(JUCE)

juce_add_plugin(MicroKeys
    COMPANY_NAME "Warren Audio"
    BUNDLE_ID "com.warrenaudio.microkeys"
    IS_SYNTH TRUE
    NEEDS_MIDI_INPUT TRUE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    COPY_PLUGIN_AFTER_BUILD FALSE
    PLUGIN_MANUFACTURER_CODE Wrna
    PLUGIN_CODE Mkey
    FORMATS VST3 Standalone
    PRODUCT_NAME "MicroKeys")

target_sources(MicroKeys PRIVATE
    Source/PluginProcessor.cpp
    Source/PluginEditor.cpp
    Source/FolderProbe.cpp)

target_compile_definitions(MicroKeys PUBLIC
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0)

target_link_libraries(MicroKeys
    PRIVATE
        juce::juce_audio_utils
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags)
