#include "PluginProcessor.h"
#include "PluginEditor.h"
#include "MicroVoice.h"

MicroKeysProcessor::MicroKeysProcessor()
    : AudioProcessor(BusesProperties().withOutput("Output", juce::AudioChannelSet::stereo(), true)),
      apvts(*this, nullptr, "Parameters", createParameterLayout())
{
    synth.addSound(new MicroSound());

    for (int i = 0; i < 16; ++i)
        synth.addVoice(new MicroVoice(tuning, apvts));
}

juce::AudioProcessorValueTreeState::ParameterLayout MicroKeysProcessor::createParameterLayout()
{
    using P = juce::AudioParameterFloat;
    juce::AudioProcessorValueTreeState::ParameterLayout layout;

    layout.add(std::make_unique<P>("gain",       "Gain",       juce::NormalisableRange<float>(-40.0f, 6.0f, 0.1f), -6.0f));
    layout.add(std::make_unique<P>("brightness", "Brightness", juce::NormalisableRange<float>(0.0f, 4.0f, 0.01f),  1.6f));
    layout.add(std::make_unique<P>("attack",     "Attack",     juce::NormalisableRange<float>(0.001f, 2.0f, 0.001f, 0.4f), 0.003f));
    layout.add(std::make_unique<P>("decay",      "Decay",      juce::NormalisableRange<float>(0.05f, 4.0f, 0.01f, 0.5f),  1.4f));
    layout.add(std::make_unique<P>("sustain",    "Sustain",    juce::NormalisableRange<float>(0.0f, 1.0f, 0.01f),  0.3f));
    layout.add(std::make_unique<P>("release",    "Release",    juce::NormalisableRange<float>(0.02f, 4.0f, 0.01f, 0.5f), 0.4f));

    return layout;
}

void MicroKeysProcessor::prepareToPlay(double sampleRate, int)
{
    synth.setCurrentPlaybackSampleRate(sampleRate);
}

bool MicroKeysProcessor::isBusesLayoutSupported(const BusesLayout& layouts) const
{
    return layouts.getMainOutputChannelSet() == juce::AudioChannelSet::stereo()
        || layouts.getMainOutputChannelSet() == juce::AudioChannelSet::mono();
}

void MicroKeysProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midi)
{
    juce::ScopedNoDenormals noDenormals;
    buffer.clear();

    keyboardState.processNextMidiBuffer(midi, 0, buffer.getNumSamples(), true);
    synth.renderNextBlock(buffer, midi, 0, buffer.getNumSamples());
}

juce::AudioProcessorEditor* MicroKeysProcessor::createEditor()
{
    return new MicroKeysEditor(*this);
}

void MicroKeysProcessor::getStateInformation(juce::MemoryBlock& destData)
{
    juce::ValueTree state("MicroKeysState");
    state.appendChild(apvts.copyState(), nullptr);

    juce::StringArray centsList;
    for (int n = 0; n < 128; ++n)
        centsList.add(juce::String(tuning.getCents(n), 4));
    state.setProperty("tuningCents", centsList.joinIntoString(","), nullptr);
    state.setProperty("scaleName", getScaleName(), nullptr);
    state.setProperty("scaleEdited", isScaleEdited(), nullptr);

    // Saved only when it isn't 12, so 12-key projects are stored exactly as before.
    if (const int n = getKeysPerOctave(); n != 12)
        state.setProperty("keysPerOctave", n, nullptr);

    juce::MemoryOutputStream stream(destData, false);
    state.writeToStream(stream);
}

void MicroKeysProcessor::setStateInformation(const void* data, int sizeInBytes)
{
    auto state = juce::ValueTree::readFromData(data, (size_t) sizeInBytes);
    if (! state.isValid())
        return;

    auto params = state.getChildWithName(apvts.state.getType());
    if (params.isValid())
        apvts.replaceState(params);

    juce::StringArray centsList;
    centsList.addTokens(state.getProperty("tuningCents").toString(), ",", "");
    for (int n = 0; n < juce::jmin(128, centsList.size()); ++n)
        tuning.setCents(n, centsList[n].getFloatValue());

    setScaleName(state.getProperty("scaleName", defaultScaleName).toString(),
                 (bool) state.getProperty("scaleEdited", false));

    // Always applied: projects saved before this setting existed have no property and
    // are 12-key layouts. Unknown values also mean 12.
    setKeysPerOctave((int) state.getProperty("keysPerOctave", 12));
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new MicroKeysProcessor();
}
