<template>
    <div class="container">
        <b-steps v-model="activeStep" :has-navigation="(false)">
            <b-step-item label="Journal Files"></b-step-item>
            <b-step-item label="Journal Metadata"></b-step-item>
            <b-step-item label="Start Import"></b-step-item>
        </b-steps>

        <div class="container" v-if="activeStep === 0">
            <ContinueButton
                @click="continueToMetadata" :disabled="!validJobFiles()">
            </ContinueButton>
            <b-notification
                type="is-danger"
                aria-close-label="Close notification"
                role="alert"
                v-if="!validJobFiles()">
                Kein Ordner gewählt, oder Ordner falsch benannt.
                Ordner müssen JOURNAL-ZID... heißen.
                (Groß/Kleinschreibung wird ignoriert)
            </b-notification>
            <JobFilesForm
                :selected-paths.sync="selectedPaths"
                :accepted-filetypes="acceptedFileTypes"
            />
            <ContinueButton class="toMetadataButton"
                @click="continueToMetadata" :disabled="!validJobFiles()">
            </ContinueButton>
        </div>
        <div class="container" v-if="activeStep === 1">
            <ContinueButton class="toOptionsButton"
                @click="continueToOptions" :disabled="hasInvalidTargets()">
            </ContinueButton>
            <JournalMetadataForm
                :selected-paths="selectedPaths"
                @update:targetsUpdated="onTargetsUpdated"
            />
            <ContinueButton class="toOptionsButton"
                @click="continueToOptions" :disabled="hasInvalidTargets()">
            </ContinueButton>
        </div>
        <div class="container" v-if="activeStep === 2">
            <StartJobButton class="startJobButton"
                @click="startJob" :disabled="hasInvalidTargets()">
            </StartJobButton>
            <JournalOptionsForm
                :initialOptions="this.parameters.options"
                @options-updated="this.parameters.options = $event"
            />
            <StartJobButton class="startJobButton"
                @click="startJob" :disabled="hasInvalidTargets()"></StartJobButton>
        </div>
    </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { startJob } from '../JobClient';

import JobFilesForm from '../JobFilesForm.vue';
import JournalMetadataForm from './IngestJournalMetadataForm.vue';
import JournalOptionsForm from './IngestJournalOptionsForm.vue';

import { JobTargetError, OCROptions } from '../JobParameters';
import {
    IngestJournalParameters, MaybeJobTarget, IngestJournalOptions
} from './IngestJournalParameters';

import { showError, showSuccess } from '@/util/Notifier';
import ContinueButton from '@/util/ContinueButton.vue';
import StartJobButton from '@/util/StartJobButton.vue';

@Component({
    components: {
        JobFilesForm,
        JournalMetadataForm,
        JournalOptionsForm,
        ContinueButton,
        StartJobButton
    }
})
export default class IngestJournal extends Vue {
    selectedPaths: string[] = [];
    acceptedFileTypes = 'image/tiff, image/tif';
    parameters: IngestJournalParameters;
    activeStep: number = 0;

    constructor() {
        super();

        const options = {
            ocr_options: {
                do_ocr: true,
                ocr_lang: 'deu'
            } as OCROptions
        } as IngestJournalOptions;

        this.parameters = new IngestJournalParameters([], options);
    }

    continueToMetadata() {
        this.activeStep = 1;
    }

    onTargetsUpdated(targets: MaybeJobTarget[]) {
        this.parameters.targets = targets;
    }

    continueToOptions() {
        this.activeStep = 2;
    }

    hasInvalidTargets() {
        return this.parameters.targets.filter(
            target => target instanceof JobTargetError
        ).length > 0 || this.parameters.targets.length === 0;
    }

    validJobFiles() {
        let pathIsValid = false;
        pathIsValid = this.selectedPaths
            .map(path => /.*JOURNAL-ZID(\d+)/i.test(path))
            .reduce((a, b) => a && b, true);
        return this.selectedPaths.length !== 0 && pathIsValid;
    }

    async startJob() {
        try {
            if (this.parameters !== undefined) {
                await startJob('ingest_journals', this.parameters);
                showSuccess('Job started');
                this.$router.push({ path: '/' });
            }
        } catch (e) {
            showError(e);
        }
    }
}
</script>

<style scoped lang="scss">
div.step-item {
    font-style: italic;
    font-size: x-large;
}
</style>
