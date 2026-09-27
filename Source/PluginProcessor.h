#pragma once

#include <juce_audio_utils/juce_audio_utils.h>
#include "TuningTable.h"

class MicroKeysProcessor : public juce::AudioProcessor
{
public:
    MicroKeysProcessor();

    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override {}
    bool isBusesLayoutSupported(const BusesLayout& layouts) const override;
    void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }

    const juce::String getName() const override { return "MicroKeys"; }
    bool acceptsMidi() const override { return true; }
    bool producesMidi() const override { return false; }
    bool isMidiEffect() const override { return false; }
    double getTailLengthSeconds() const override { return 2.0; }

    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram(int) override {}
    const juce::String getProgramName(int) override { return {}; }
    void changeProgramName(int, const juce::String&) override {}

    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;

    TuningTable tuning;
    juce::MidiKeyboardState keyboardState;
    juce::AudioProcessorValueTreeState apvts;

    // Name of the currently loaded scale, shown in the editor. Guarded because
    // state save/restore may run off the message thread.
    juce::String getScaleName() const
    {
        const juce::ScopedLock sl(scaleNameLock);
        return scaleName;
    }

    void setScaleName(const juce::String& newName, bool edited = false)
    {
        const juce::ScopedLock sl(scaleNameLock);
        scaleName = newName;
        scaleEdited.store(edited);
    }

    void markScaleEdited() { scaleEdited.store(true); }
    bool isScaleEdited() const { return scaleEdited.load(); }

    static constexpr const char* defaultScaleName = "Standard tuning (12-TET)";

private:
    static juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();

    juce::Synthesiser synth;

    juce::String scaleName { defaultScaleName };
    std::atomic<bool> scaleEdited { false };
    juce::CriticalSection scaleNameLock;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MicroKeysProcessor)
};
