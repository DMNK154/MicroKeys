#pragma once

#include <juce_audio_utils/juce_audio_utils.h>
#include "TuningTable.h"

struct MicroSound : public juce::SynthesiserSound
{
    bool appliesToNote(int) override { return true; }
    bool appliesToChannel(int) override { return true; }
};

// A simple 2-operator FM voice with a warm electric-piano character.
// The oscillator frequency is re-read from the tuning table every block,
// so dragging the tuning slider retunes notes that are already sounding.
class MicroVoice : public juce::SynthesiserVoice
{
public:
    MicroVoice(const TuningTable& tuningTable, juce::AudioProcessorValueTreeState& state)
        : tuning(tuningTable), apvts(state)
    {
    }

    bool canPlaySound(juce::SynthesiserSound* sound) override
    {
        return dynamic_cast<MicroSound*>(sound) != nullptr;
    }

    void startNote(int midiNoteNumber, float velocity, juce::SynthesiserSound*, int) override
    {
        note = midiNoteNumber;
        vel = velocity;
        carrierPhase = 0.0;
        modPhase = 0.0;
        modEnv = 1.0f;

        adsr.setSampleRate(getSampleRate());
        juce::ADSR::Parameters p;
        p.attack  = *apvts.getRawParameterValue("attack");
        p.decay   = *apvts.getRawParameterValue("decay");
        p.sustain = *apvts.getRawParameterValue("sustain");
        p.release = *apvts.getRawParameterValue("release");
        adsr.setParameters(p);
        adsr.noteOn();

        // The FM index (brightness) decays over ~400 ms for a plucked/struck attack.
        modEnvDecay = (float) std::exp(-1.0 / (0.4 * getSampleRate()));
    }

    void stopNote(float, bool allowTailOff) override
    {
        if (allowTailOff)
        {
            adsr.noteOff();
        }
        else
        {
            adsr.reset();
            clearCurrentNote();
        }
    }

    void pitchWheelMoved(int) override {}
    void controllerMoved(int, int) override {}

    void renderNextBlock(juce::AudioBuffer<float>& output, int startSample, int numSamples) override
    {
        if (! adsr.isActive())
            return;

        const double freq = tuning.frequencyForNote(note);
        const double sr = getSampleRate();
        const double carrierInc = juce::MathConstants<double>::twoPi * freq / sr;
        const double modInc = carrierInc; // 1:1 ratio keeps sidebands harmonic

        const float brightness = *apvts.getRawParameterValue("brightness");
        const float gain = juce::Decibels::decibelsToGain((float) *apvts.getRawParameterValue("gain"));
        const float index = brightness * (0.5f + vel);

        for (int i = 0; i < numSamples; ++i)
        {
            modEnv *= modEnvDecay;

            const float mod = std::sin((float) modPhase) * index * modEnv;
            const float sample = std::sin((float) carrierPhase + mod)
                               * adsr.getNextSample() * vel * gain * 0.4f;

            for (int ch = 0; ch < output.getNumChannels(); ++ch)
                output.addSample(ch, startSample + i, sample);

            carrierPhase += carrierInc;
            modPhase += modInc;

            if (carrierPhase > juce::MathConstants<double>::twoPi)
                carrierPhase -= juce::MathConstants<double>::twoPi;
            if (modPhase > juce::MathConstants<double>::twoPi)
                modPhase -= juce::MathConstants<double>::twoPi;
        }

        if (! adsr.isActive())
            clearCurrentNote();
    }

private:
    const TuningTable& tuning;
    juce::AudioProcessorValueTreeState& apvts;

    int note = 60;
    float vel = 0.0f;
    double carrierPhase = 0.0;
    double modPhase = 0.0;
    float modEnv = 1.0f;
    float modEnvDecay = 0.9999f;
    juce::ADSR adsr;
};
