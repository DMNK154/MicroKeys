#pragma once

#include <array>
#include <cmath>
#include <juce_audio_utils/juce_audio_utils.h>
#include "PluginProcessor.h"

// Opens a combo box's list inside the plugin window instead of as a separate
// desktop window, which some hosts and multi-monitor setups fail to show or click.
struct InWindowMenuLookAndFeel : juce::LookAndFeel_V4
{
    juce::PopupMenu::Options getOptionsForComboBoxPopupMenu(juce::ComboBox& box, juce::Label& label) override
    {
        auto options = juce::LookAndFeel_V4::getOptionsForComboBoxPopupMenu(box, label);
        if (auto* editor = box.findParentComponentOfClass<juce::AudioProcessorEditor>())
            return options.withParentComponent(editor);
        return options;
    }
};

// The on-screen keyboard. When an octave is not 12 keys and "Tune all octaves" is on, it
// tints the selected key and every key a change to it also retunes (the keys N apart).
// With 12 keys per octave, or the toggle off, it draws exactly like the plain keyboard.
class OctaveChainKeyboard : public juce::MidiKeyboardComponent
{
public:
    using juce::MidiKeyboardComponent::MidiKeyboardComponent;

    void showChain(int selectedNote, int keysPerOctave, bool tuneAllOctaves)
    {
        const int step = (tuneAllOctaves && keysPerOctave != 12) ? keysPerOctave : 0; // 0: no tint
        if (step == chainStep && (step == 0 || selectedNote == chainNote))
            return;

        chainNote = selectedNote;
        chainStep = step;
        repaint();
    }

    void drawWhiteNote(int midiNoteNumber, juce::Graphics& g, juce::Rectangle<float> area,
                       bool isDown, bool isOver, juce::Colour lineColour, juce::Colour textColour) override
    {
        tintIfInChain(midiNoteNumber, g, area); // under the key-down overlay, text and lines
        juce::MidiKeyboardComponent::drawWhiteNote(midiNoteNumber, g, area, isDown, isOver, lineColour, textColour);
    }

    void drawBlackNote(int midiNoteNumber, juce::Graphics& g, juce::Rectangle<float> area,
                       bool isDown, bool isOver, juce::Colour noteFillColour) override
    {
        juce::MidiKeyboardComponent::drawBlackNote(midiNoteNumber, g, area, isDown, isOver, noteFillColour);
        tintIfInChain(midiNoteNumber, g, area); // black keys are opaque, so tint on top
    }

private:
    void tintIfInChain(int note, juce::Graphics& g, juce::Rectangle<float> area) const
    {
        if (chainStep > 0 && (note - chainNote) % chainStep == 0)
        {
            g.setColour(juce::Colours::orange.withAlpha(0.45f));
            g.fillRect(area);
        }
    }

    int chainNote = -1;
    int chainStep = 0;
};

class MicroKeysEditor : public juce::AudioProcessorEditor,
                        private juce::MidiKeyboardState::Listener,
                        private juce::Timer
{
public:
    explicit MicroKeysEditor(MicroKeysProcessor&);
    ~MicroKeysEditor() override;

    void paint(juce::Graphics&) override;
    void resized() override;

private:
    void handleNoteOn(juce::MidiKeyboardState*, int channel, int note, float velocity) override;
    void handleNoteOff(juce::MidiKeyboardState*, int, int, float) override {}
    void timerCallback() override;
    void updateScaleLabel();

    void selectNote(int note);
    void applyCentsFromSlider();
    void applyHz(int note, double hz);
    void refreshReadouts();
    void refreshGrid();
    int gridBaseNote() const;
    void saveScale();
    void loadScale();
    void importScala(const juce::File& file);
    static juce::File scalesFolder();
    static juce::File dialogFolder(); // where Save and Load open: the folder last used
    static void rememberDialogFolder(const juce::File& chosenFile);

    void stepOctave(int delta);

    void syncKeysPerOctave();    // show the processor's Keys per octave; never retunes
    void updateKeyboardChain();  // tint the keys "Tune all octaves" ties together

    MicroKeysProcessor& processor;
    InWindowMenuLookAndFeel inWindowMenus; // must outlive octaveBox and keysPerOctaveBox

    int selectedNote = 69; // A4
    int shownKeysPerOctave = 0; // what the UI currently shows; 0 until the first sync

    juce::Label titleLabel, scaleNameLabel, selectedNoteLabel, freqLabel, hintLabel, noticeLabel;
    juce::Label keysPerOctaveLabel;
    juce::ComboBox keysPerOctaveBox;
    juce::Slider centsSlider;
    juce::ToggleButton allOctavesToggle { "Tune all octaves (like a string)" };
    juce::TextButton resetKeyButton { "Reset key" }, resetAllButton { "Reset all" };
    juce::TextButton saveScaleButton { "Save scale..." }, loadScaleButton { "Load scale..." };
    std::unique_ptr<juce::FileChooser> fileChooser;

    juce::Label gridCaption, octaveLabel;
    juce::ComboBox octaveBox;
    juce::TextButton octaveDownButton { "<" }, octaveUpButton { ">" };
    std::array<juce::Label, 12> gridLabels;
    std::array<juce::TextEditor, 12> hzBoxes;

    juce::Slider gainSlider, brightnessSlider, attackSlider, decaySlider, sustainSlider, releaseSlider;
    juce::Label gainLabel, brightnessLabel, attackLabel, decayLabel, sustainLabel, releaseLabel;

    using Attachment = juce::AudioProcessorValueTreeState::SliderAttachment;
    std::unique_ptr<Attachment> gainAtt, brightnessAtt, attackAtt, decayAtt, sustainAtt, releaseAtt;

    OctaveChainKeyboard keyboard;

    // Shows tooltips inside the plugin window. It is a child of the editor, not a separate
    // desktop window, which some hosts and multi-monitor setups fail to show.
    juce::TooltipWindow tooltipWindow { this };

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MicroKeysEditor)
};
