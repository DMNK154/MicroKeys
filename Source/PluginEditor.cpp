#include "PluginEditor.h"
#include "ScalaScale.h"

MicroKeysEditor::MicroKeysEditor(MicroKeysProcessor& p)
    : AudioProcessorEditor(&p),
      processor(p),
      keyboard(p.keyboardState, juce::MidiKeyboardComponent::horizontalKeyboard)
{
    titleLabel.setText(juce::String(juce::CharPointer_UTF8("MicroKeys \xe2\x80\x94 per-key tuning")),
                       juce::dontSendNotification);
    titleLabel.setFont(juce::FontOptions(22.0f, juce::Font::bold));
    addAndMakeVisible(titleLabel);

    scaleNameLabel.setFont(juce::FontOptions(16.0f, juce::Font::bold));
    scaleNameLabel.setJustificationType(juce::Justification::centredRight);
    scaleNameLabel.setColour(juce::Label::textColourId, juce::Colours::orange);
    addAndMakeVisible(scaleNameLabel);

    hintLabel.setText("Play or click a key to select it, drag the slider to tune by ear, or type an exact Hz value below and press Enter.",
                      juce::dontSendNotification);
    hintLabel.setFont(juce::FontOptions(13.0f));
    hintLabel.setColour(juce::Label::textColourId, juce::Colours::grey);
    addAndMakeVisible(hintLabel);

    selectedNoteLabel.setFont(juce::FontOptions(18.0f, juce::Font::bold));
    addAndMakeVisible(selectedNoteLabel);

    freqLabel.setFont(juce::FontOptions(15.0f));
    addAndMakeVisible(freqLabel);

    centsSlider.setSliderStyle(juce::Slider::LinearHorizontal);
    centsSlider.setRange(-200.0, 200.0, 0.001);
    centsSlider.setNumDecimalPlacesToDisplay(2);
    centsSlider.setTextBoxStyle(juce::Slider::TextBoxRight, false, 90, 24);
    centsSlider.setTextValueSuffix(" ct");
    centsSlider.setDoubleClickReturnValue(true, 0.0);
    centsSlider.onValueChange = [this] { applyCentsFromSlider(); };
    addAndMakeVisible(centsSlider);

    allOctavesToggle.setToggleState(true, juce::dontSendNotification);
    addAndMakeVisible(allOctavesToggle);

    resetKeyButton.onClick = [this]
    {
        centsSlider.setValue(0.0); // triggers applyCentsFromSlider
    };
    addAndMakeVisible(resetKeyButton);

    resetAllButton.onClick = [this]
    {
        processor.tuning.resetAll();
        processor.setScaleName(MicroKeysProcessor::defaultScaleName);
        centsSlider.setValue(0.0, juce::dontSendNotification);
        refreshReadouts();
    };
    addAndMakeVisible(resetAllButton);

    saveScaleButton.onClick = [this] { saveScale(); };
    addAndMakeVisible(saveScaleButton);

    loadScaleButton.onClick = [this] { loadScale(); };
    addAndMakeVisible(loadScaleButton);

    gridCaption.setText("Exact Hz per key (type a value, press Enter)", juce::dontSendNotification);
    gridCaption.setFont(juce::FontOptions(14.0f, juce::Font::bold));
    addAndMakeVisible(gridCaption);

    octaveLabel.setText("Octave:", juce::dontSendNotification);
    octaveLabel.setJustificationType(juce::Justification::centredRight);
    addAndMakeVisible(octaveLabel);

    for (int o = 0; o <= 8; ++o)
        octaveBox.addItem("C" + juce::String(o), o + 1);
    octaveBox.setSelectedId(5, juce::dontSendNotification); // octave 4
    octaveBox.onChange = [this] { refreshGrid(); };
    octaveBox.setLookAndFeel(&inWindowMenus);
    addAndMakeVisible(octaveBox);

    octaveDownButton.setTooltip("Previous octave");
    octaveDownButton.onClick = [this] { stepOctave(-1); };
    addAndMakeVisible(octaveDownButton);

    octaveUpButton.setTooltip("Next octave");
    octaveUpButton.onClick = [this] { stepOctave(1); };
    addAndMakeVisible(octaveUpButton);

    for (int i = 0; i < 12; ++i)
    {
        auto& label = gridLabels[(size_t) i];
        label.setJustificationType(juce::Justification::centred);
        label.setFont(juce::FontOptions(13.0f));
        addAndMakeVisible(label);

        auto& box = hzBoxes[(size_t) i];
        box.setInputRestrictions(12, "0123456789.");
        box.setJustification(juce::Justification::centred);
        box.setSelectAllWhenFocused(true);

        auto commit = [this, i]
        {
            const int note = gridBaseNote() + i;
            const auto typed = hzBoxes[(size_t) i].getText();
            const double hz = typed.getDoubleValue();

            // Skip if the text is just the value we displayed — re-applying the
            // rounded display string would erode the stored precision.
            if (note <= 127 && typed == juce::String(processor.tuning.frequencyForNote(note), 3))
                return;

            if (note <= 127 && hz > 0.0)
                applyHz(note, hz);
            else
                refreshGrid(); // restore the previous value
        };
        box.onReturnKey = commit;
        box.onFocusLost = commit;
        box.onEscapeKey = [this] { refreshGrid(); };

        addAndMakeVisible(box);
    }

    auto setupKnob = [this](juce::Slider& s, juce::Label& l, const juce::String& name,
                            std::unique_ptr<Attachment>& att, const juce::String& paramID)
    {
        s.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
        s.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 60, 18);
        addAndMakeVisible(s);
        l.setText(name, juce::dontSendNotification);
        l.setJustificationType(juce::Justification::centred);
        l.setFont(juce::FontOptions(13.0f));
        addAndMakeVisible(l);
        att = std::make_unique<Attachment>(processor.apvts, paramID, s);
    };

    setupKnob(gainSlider,       gainLabel,       "Gain",       gainAtt,       "gain");
    setupKnob(brightnessSlider, brightnessLabel, "Brightness", brightnessAtt, "brightness");
    setupKnob(attackSlider,     attackLabel,     "Attack",     attackAtt,     "attack");
    setupKnob(decaySlider,      decayLabel,      "Decay",      decayAtt,      "decay");
    setupKnob(sustainSlider,    sustainLabel,    "Sustain",    sustainAtt,    "sustain");
    setupKnob(releaseSlider,    releaseLabel,    "Release",    releaseAtt,    "release");

    keyboard.setAvailableRange(21, 108); // 88 keys
    addAndMakeVisible(keyboard);

    noticeLabel.setText("MicroKeys " JucePlugin_VersionString " - free software under the GNU AGPLv3, with no warranty - "
                        "github.com/DMNK154/MicroKeys\n"
                        "VST is a trademark of Steinberg Media Technologies GmbH, registered in Europe and other countries.",
                        juce::dontSendNotification);
    noticeLabel.setFont(juce::FontOptions(11.0f));
    noticeLabel.setJustificationType(juce::Justification::centred);
    noticeLabel.setColour(juce::Label::textColourId, juce::Colours::grey);
    addAndMakeVisible(noticeLabel);

    processor.keyboardState.addListener(this);

    selectNote(selectedNote);
    updateScaleLabel();
    startTimerHz(2); // keep the label fresh if the host restores state while open
    setSize(820, 592);
}

MicroKeysEditor::~MicroKeysEditor()
{
    octaveBox.setLookAndFeel(nullptr);
    processor.keyboardState.removeListener(this);
}

void MicroKeysEditor::stepOctave(int delta)
{
    const int id = juce::jlimit(1, octaveBox.getNumItems(), octaveBox.getSelectedId() + delta);
    octaveBox.setSelectedId(id, juce::sendNotificationSync);
}

void MicroKeysEditor::handleNoteOn(juce::MidiKeyboardState*, int, int note, float)
{
    // May be called from the audio thread — hop to the message thread before touching UI.
    juce::MessageManager::callAsync([safeThis = juce::Component::SafePointer<MicroKeysEditor>(this), note]
    {
        if (safeThis != nullptr)
            safeThis->selectNote(note);
    });
}

void MicroKeysEditor::selectNote(int note)
{
    selectedNote = juce::jlimit(0, 127, note);

    // Keep the slider at +/-200 ct for fine work, but widen it when this key
    // has been remapped further so it always shows the true value.
    const auto cents = processor.tuning.getCents(selectedNote);
    const double limit = juce::jmax(200.0, std::ceil(std::abs((double) cents) / 100.0) * 100.0);
    centsSlider.setRange(-limit, limit, 0.001);
    centsSlider.setValue(cents, juce::dontSendNotification);

    // Follow the played key so its Hz box is always on screen.
    octaveBox.setSelectedId(juce::jlimit(1, 9, selectedNote / 12), juce::dontSendNotification);

    refreshReadouts();
}

void MicroKeysEditor::applyHz(int note, double hz)
{
    hz = juce::jlimit(1.0, 20000.0, hz);
    const double standard = 440.0 * std::pow(2.0, (note - 69) / 12.0);
    const auto cents = (float) (1200.0 * std::log2(hz / standard));

    if (allOctavesToggle.getToggleState())
        processor.tuning.setCentsAllOctaves(note, cents);
    else
        processor.tuning.setCents(note, cents);

    processor.markScaleEdited();
    selectNote(note);
}

juce::File MicroKeysEditor::scalesFolder()
{
    auto dir = juce::File::getSpecialLocation(juce::File::userDocumentsDirectory)
                   .getChildFile("MicroKeys Scales");
    dir.createDirectory();
    return dir;
}

void MicroKeysEditor::saveScale()
{
    fileChooser = std::make_unique<juce::FileChooser>(
        "Save scale", scalesFolder().getChildFile("MyScale.mkscale"), "*.mkscale");

    fileChooser->launchAsync(juce::FileBrowserComponent::saveMode
                                 | juce::FileBrowserComponent::canSelectFiles
                                 | juce::FileBrowserComponent::warnAboutOverwriting,
        [this](const juce::FileChooser& fc)
        {
            auto file = fc.getResult();
            if (file == juce::File())
                return;

            file = file.withFileExtension(".mkscale");

            juce::XmlElement xml("MicroKeysScale");
            for (int n = 0; n < 128; ++n)
            {
                const auto cents = processor.tuning.getCents(n);
                if (cents != 0.0f)
                {
                    auto* key = xml.createNewChildElement("Key");
                    key->setAttribute("note", n);
                    key->setAttribute("cents", (double) cents);
                }
            }

            if (! xml.writeTo(file))
            {
                juce::NativeMessageBox::showAsync(juce::MessageBoxOptions()
                                                      .withIconType(juce::MessageBoxIconType::WarningIcon)
                                                      .withTitle("Save failed")
                                                      .withMessage("Could not write " + file.getFullPathName())
                                                      .withButton("OK")
                                                      .withAssociatedComponent(this),
                                                  nullptr);
                return;
            }

            processor.setScaleName(file.getFileNameWithoutExtension());
            updateScaleLabel();
        });
}

void MicroKeysEditor::loadScale()
{
    fileChooser = std::make_unique<juce::FileChooser>("Load scale (.mkscale or Scala .scl)",
                                                      scalesFolder(), "*.mkscale;*.scl");

    fileChooser->launchAsync(juce::FileBrowserComponent::openMode
                                 | juce::FileBrowserComponent::canSelectFiles,
        [this](const juce::FileChooser& fc)
        {
            auto file = fc.getResult();
            if (file == juce::File()) // dialog cancelled
                return;

            if (! file.existsAsFile())
            {
                juce::NativeMessageBox::showAsync(juce::MessageBoxOptions()
                                                      .withIconType(juce::MessageBoxIconType::WarningIcon)
                                                      .withTitle("Load failed")
                                                      .withMessage("File not found or not readable:\n" + file.getFullPathName())
                                                      .withButton("OK")
                                                      .withAssociatedComponent(this),
                                                  nullptr);
                return;
            }

            if (file.getFileExtension().equalsIgnoreCase(".scl"))
            {
                importScala(file);
                return;
            }

            auto xml = juce::parseXML(file);
            if (xml == nullptr || ! xml->hasTagName("MicroKeysScale"))
            {
                juce::NativeMessageBox::showAsync(juce::MessageBoxOptions()
                                                      .withIconType(juce::MessageBoxIconType::WarningIcon)
                                                      .withTitle("Load failed")
                                                      .withMessage(file.getFileName() + " is not a MicroKeys scale file.")
                                                      .withButton("OK")
                                                      .withAssociatedComponent(this),
                                                  nullptr);
                return;
            }

            processor.tuning.resetAll();
            for (auto* key : xml->getChildWithTagNameIterator("Key"))
                processor.tuning.setCents(key->getIntAttribute("note"),
                                          (float) key->getDoubleAttribute("cents"));

            processor.setScaleName(file.getFileNameWithoutExtension());
            selectNote(selectedNote); // refresh slider, readouts and Hz grid
        });
}

void MicroKeysEditor::importScala(const juce::File& file)
{
    const auto text = file.loadFileAsString();
    if (text.isEmpty())
    {
        juce::NativeMessageBox::showAsync(juce::MessageBoxOptions()
                                              .withIconType(juce::MessageBoxIconType::WarningIcon)
                                              .withTitle("Scala import failed")
                                              .withMessage("Could not read any data from:\n" + file.getFullPathName()
                                                           + "\n\nIf this file is in OneDrive, it may be cloud-only. "
                                                             "Right-click it and choose \"Always keep on this device\".")
                                              .withButton("OK")
                                              .withAssociatedComponent(this),
                                          nullptr);
        return;
    }

    juce::String error;
    auto scale = ScalaScale::parse(text, error);

    if (scale == nullptr)
    {
        juce::NativeMessageBox::showAsync(juce::MessageBoxOptions()
                                              .withIconType(juce::MessageBoxIconType::WarningIcon)
                                              .withTitle("Scala import failed")
                                              .withMessage(error)
                                              .withButton("OK")
                                              .withAssociatedComponent(this),
                                          nullptr);
        return;
    }

    scale->applyToTable(processor.tuning, selectedNote);
    processor.setScaleName(file.getFileNameWithoutExtension());
    selectNote(selectedNote);

    const auto rootName = juce::MidiMessage::getMidiNoteName(selectedNote, true, true, 4);
    juce::NativeMessageBox::showAsync(
        juce::MessageBoxOptions()
            .withIconType(juce::MessageBoxIconType::InfoIcon)
            .withTitle("Scala scale loaded")
            .withMessage((scale->description.isNotEmpty() ? scale->description + "\n\n" : juce::String())
                         + juce::String(scale->notesPerPeriod()) + " notes per period ("
                         + juce::String(scale->periodCents, 2) + " cents), root 1/1 on "
                         + rootName + " at "
                         + juce::String(processor.tuning.frequencyForNote(selectedNote), 3) + " Hz.")
            .withButton("OK")
            .withAssociatedComponent(this),
        nullptr);
}

int MicroKeysEditor::gridBaseNote() const
{
    return octaveBox.getSelectedId() * 12; // id 1 -> octave 0 -> C0 = MIDI 12
}

void MicroKeysEditor::refreshGrid()
{
    const int base = gridBaseNote();

    for (int i = 0; i < 12; ++i)
    {
        const int note = base + i;
        auto& box = hzBoxes[(size_t) i];
        auto& label = gridLabels[(size_t) i];

        if (note > 127)
        {
            box.setEnabled(false);
            box.setText({}, juce::dontSendNotification);
            label.setText({}, juce::dontSendNotification);
            continue;
        }

        box.setEnabled(true);
        box.setText(juce::String(processor.tuning.frequencyForNote(note), 3),
                    juce::dontSendNotification);
        label.setText(juce::MidiMessage::getMidiNoteName(note, true, true, 4),
                      juce::dontSendNotification);

        const bool isSelected = (note == selectedNote);
        box.setColour(juce::TextEditor::outlineColourId,
                      isSelected ? juce::Colours::orange
                                 : getLookAndFeel().findColour(juce::TextEditor::outlineColourId));
        box.repaint();
    }
}

void MicroKeysEditor::applyCentsFromSlider()
{
    const auto value = (float) centsSlider.getValue();

    if (allOctavesToggle.getToggleState())
        processor.tuning.setCentsAllOctaves(selectedNote, value);
    else
        processor.tuning.setCents(selectedNote, value);

    processor.markScaleEdited();
    refreshReadouts();
}

void MicroKeysEditor::updateScaleLabel()
{
    scaleNameLabel.setText(processor.getScaleName()
                               + (processor.isScaleEdited() ? " (edited)" : ""),
                           juce::dontSendNotification);
}

void MicroKeysEditor::refreshReadouts()
{
    const auto name = juce::MidiMessage::getMidiNoteName(selectedNote, true, true, 4);
    selectedNoteLabel.setText("Key: " + name, juce::dontSendNotification);

    const auto freq = processor.tuning.frequencyForNote(selectedNote);
    const auto cents = processor.tuning.getCents(selectedNote);
    freqLabel.setText(juce::String(freq, 3) + " Hz  (" + (cents >= 0 ? "+" : "")
                          + juce::String(cents, 2) + " cents)",
                      juce::dontSendNotification);

    refreshGrid();
    updateScaleLabel();
}

void MicroKeysEditor::paint(juce::Graphics& g)
{
    g.fillAll(getLookAndFeel().findColour(juce::ResizableWindow::backgroundColourId));
}

void MicroKeysEditor::resized()
{
    auto area = getLocalBounds().reduced(16);

    auto titleRow = area.removeFromTop(30);
    titleLabel.setBounds(titleRow.removeFromLeft(320));
    scaleNameLabel.setBounds(titleRow);
    hintLabel.setBounds(area.removeFromTop(22));
    area.removeFromTop(8);

    auto tuningRow = area.removeFromTop(30);
    selectedNoteLabel.setBounds(tuningRow.removeFromLeft(140));
    freqLabel.setBounds(tuningRow);

    centsSlider.setBounds(area.removeFromTop(36));
    area.removeFromTop(6);

    auto buttonRow = area.removeFromTop(28);
    allOctavesToggle.setBounds(buttonRow.removeFromLeft(270));
    buttonRow.removeFromLeft(10);
    resetKeyButton.setBounds(buttonRow.removeFromLeft(90));
    buttonRow.removeFromLeft(8);
    resetAllButton.setBounds(buttonRow.removeFromLeft(90));
    buttonRow.removeFromLeft(20);
    saveScaleButton.setBounds(buttonRow.removeFromLeft(110));
    buttonRow.removeFromLeft(8);
    loadScaleButton.setBounds(buttonRow.removeFromLeft(110));
    area.removeFromTop(12);

    auto knobRow = area.removeFromTop(110);
    juce::Slider* knobs[] = { &gainSlider, &brightnessSlider, &attackSlider,
                              &decaySlider, &sustainSlider, &releaseSlider };
    juce::Label* labels[] = { &gainLabel, &brightnessLabel, &attackLabel,
                              &decayLabel, &sustainLabel, &releaseLabel };
    const int knobWidth = knobRow.getWidth() / 6;

    for (int i = 0; i < 6; ++i)
    {
        auto cell = knobRow.removeFromLeft(knobWidth);
        labels[i]->setBounds(cell.removeFromTop(18));
        knobs[i]->setBounds(cell.reduced(6, 0));
    }

    area.removeFromTop(6);
    auto captionRow = area.removeFromTop(24);
    gridCaption.setBounds(captionRow.removeFromLeft(330));
    octaveLabel.setBounds(captionRow.removeFromLeft(70));
    captionRow.removeFromLeft(6);
    octaveDownButton.setBounds(captionRow.removeFromLeft(26));
    captionRow.removeFromLeft(4);
    octaveBox.setBounds(captionRow.removeFromLeft(80).reduced(0, 1));
    captionRow.removeFromLeft(4);
    octaveUpButton.setBounds(captionRow.removeFromLeft(26));
    area.removeFromTop(4);

    auto gridRow = area.removeFromTop(48);
    const int cellWidth = gridRow.getWidth() / 12;
    for (int i = 0; i < 12; ++i)
    {
        auto cell = gridRow.removeFromLeft(cellWidth);
        gridLabels[(size_t) i].setBounds(cell.removeFromTop(18));
        hzBoxes[(size_t) i].setBounds(cell.reduced(3, 2));
    }

    noticeLabel.setBounds(area.removeFromBottom(28));
    area.removeFromBottom(4);
    area.removeFromTop(8);
    keyboard.setBounds(area);
}
