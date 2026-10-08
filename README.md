Image Compression Tool
======================

A desktop GUI for compressing images with **visual quality control and measurable results**.

Most image compression tools reduce the process to a few presets like *Low*, *Medium*, or *High* quality. That can make it difficult to know what you're actually getting: how much space was saved, where artifacts were introduced, or whether an image could have been compressed further without noticeably affecting its quality.

This tool takes a more hands-on approach. Instead of compressing a large collection of images blindly and inspecting the results afterward, you can work through images individually, compare the original and compressed versions side by side, and decide whether the result is acceptable before saving it.

Features
--------
-   **Dual-Pane Comparison Viewer:** View your original and compressed images side-by-side with fully synced zoom and panning to easily hunt for artifacts.
-   **Position Swapping:** Instantly swap the left and right image positions to better train your eyes on subtle differences.
-   **Error Heatmap:** Visually highlight exact areas where the compressed image diverges from the original.
-   **Fine-Tuned Control:** Adjust compression levels per image for high-risk or important photos, trading raw speed for absolute safety.
-   **Quality Metrics (PSNR & SSIM):** Keep track of objective mathematical image quality scores during your session.
-   **Session Analytics:** Monitor overall compression stats (including mean and median savings) in real time.
-   **Keyboard Shortcuts:** Speed up your workflow with intuitive keybindings for quick reviewing and saving.
-   **One-Touch Saving:** Instantly save approved compressed images to your destination directory keeping original filenames intact.

The goal is to make image compression **fast enough to use interactively while keeping the decision-making process under your control**. The original image is never replaced during the compression workflow, so you can inspect the result before committing to it.

Why this approach?
------------------

Image compression is inherently a trade-off between **file size and image quality**. A higher compression level may save significantly more space, but can also introduce artifacts that aren't obvious from file size alone.

Rather than treating compression as a one-click operation, this tool provides both **visual and numerical feedback** so you can make that trade-off on an image-by-image basis.

The workflow is essentially:

**Select → Compress → Compare → Inspect → Save**

This is intentionally more cautious than a fully automated bulk compressor, but makes it much easier to avoid accidentally accepting poor-quality results.

Session Statistics
------------------

The tool keeps track of compression results across the current session, allowing you to see how the selected compression settings perform across a collection of images.

Planned/ongoing functionality includes:

-   An **Excel-like compression data viewer** for inspecting individual image statistics.
-   **CSV export** of compression data.
-   A **bulk compression wizard** for automating the process once suitable compression settings have been established.

Roadmap & Upcoming features
---------------------------

The tool is currently under active development. The interactive compression and comparison workflow is the core of the application, with additional data analysis and bulk-processing features being added around it.

The long-term goal is to provide a practical middle ground between **fully manual image optimization** and **blind bulk compression**: enough automation to make the process quick, while retaining enough control to verify that important images haven't been unnecessarily degraded.

-   **Spreadsheet Session Viewer:** An in-app table view of your compression data with direct CSV export capabilities.
-   **Bulk Compression Wizard:** A guided multi-step tool for batch processing folders when you want automation combined with safety checkpoints.

## Todo
- [ ] create "save as" option, so that user can save the file with custom name
- [x] add indefinite progress bad under the viewer, to indicate background task
- [ ] create data view. A excel like view in a popup window, that shows the data of all the files that were compressed
- [x] change the listbox to a treeview, and show a check mark for the files that are already saved

### UI changes
#### Pass 1 --- Rename things

- [ ] Change **`Try`** → **`Preview`**
- [ ] Change **`Save`** → **`Save Compressed Image`**
- [ ] Change **`Heatmap Gain`** → **`Heatmap Intensity`**
- [ ] Change **`Swap Layout`** → **`Swap Images`**
- [ ] Change **`Current File Stats & Metrics`** → **`Compression Results`**
- [ ] Change **`Overall Session Stats`** → **`Session Summary`**

#### Pass 2 --- Make the important result obvious

In `Compression Results`, instead of having everything look like a text dump:

```
Original Size: 1404.71 KB
Compressed Size: 680.25 KB
Saved Space: 51.6%
PSNR: 41.92 dB
SSIM: 0.9996

```

make the first three roughly:

```
Original       Compressed
1.37 MB   →    680 KB

51.6% smaller

```

Then put PSNR and SSIM underneath.

#### Pass 3 --- Group the bottom controls

Change the current collection of controls into:

```
VIEW
Zoom    Reset    Rotate

COMPARE
Swap Images    Heatmap    Intensity

```

You don't need to change their functionality---just visually put related controls together.

#### Pass 4 --- Make Save visually different

Make **Save Compressed Image** a large, obvious button.

Don't change the rest of the application to colorful buttons. Just make this one stand out.

#### Pass 5 --- Give the image viewer more room

If possible:

-   reduce the width of the left file list slightly
-   reduce the width of the right settings panel slightly
-   give those pixels to the center image viewer

The center viewer is where users will spend most of their time.

#### Pass 6 --- Don't redesign everything

Seriously. Don't throw away the current UI.

You've already got a sensible application layout. I'd make these incremental changes first, use the application for a while, and then decide what actually annoys you.

