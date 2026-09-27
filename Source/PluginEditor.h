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
    void timerCallback() override { updateScaleLabel(); }
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

    void stepOctave(int delta);

    MicroKeysProcessor& processor;
    InWindowMenuLookAndFeel inWindowMenus; // must outlive octaveBox

    int selectedNote = 69; // A4

    juce::Label titleLabel, scaleNameLabel, selectedNoteLabel, freqLabel, hintLabel, noticeLabel;
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

    juce::MidiKeyboardComponent keyboard;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MicroKeysEditor)
};
