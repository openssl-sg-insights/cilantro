<template>
    <section>
    <b-loading :is-full-page="false"
        :active="this.targets.length === 0"
    ></b-loading>
    <b-table v-if="this.targets.length !== 0" :data="this.targets" detailed detail-key="id">
        <template slot-scope="props">
            <b-table-column style="vertical-align: middle;">
                <b-icon v-if="isTargetError(props.row)" icon="alert-circle" type="is-danger" />
                <template v-else>
                    <b-icon
                        v-if="!props.row.metadata"
                        icon="loading"
                        custom-class="mdi-spin"/>
                    <b-icon
                        v-else
                        icon="check"
                        type="is-success"
                    />
                </template>
            </b-table-column>
            <b-table-column
                field="id"
                label="Path"
            >{{ props.row.id }}</b-table-column>
            <template
                v-if="!isTargetError(props.row) &&
                    props.row.metadata">
                <b-table-column field="metadata.title"
                                label="Title">
                    <a :href="'https://zenon.dainst.org/Record/' + props.row.metadata.zenon_id"
                       target="_blank">
                        {{ props.row.metadata.title || '-' | truncate(80) }}
                    </a>
                </b-table-column>
                <b-table-column
                    field="metadata.subtitle"
                    label="Subtitle"
                >{{ props.row.metadata.subtitle || '-' }}
                </b-table-column>
                <b-table-column
                    field="metadata.date_published"
                    label="Date published"
                    >{{ props.row.metadata.date_published || '-' }}
                </b-table-column>
            </template>
            <template v-else>
                <b-table-column label="Title">-</b-table-column>
                <b-table-column label="Subtitle">-</b-table-column>
                <b-table-column label="Date published">-</b-table-column>
            </template>
            <b-table-column label="">
                <b-button title="Remove from selection"
                            type="is-text"
                            @click="removeTarget(props.row)">
                    <b-icon icon="close"/>
                </b-button>
            </b-table-column>
        </template>

        <template slot="detail" slot-scope="props">
            <div class="content">
                <ul>
                    <li v-for="(id, name) in props.row.metadata" v-bind:key="name">
                        {{name}}: {{id}}
                    </li>
                </ul>
                <ul v-if="isTargetError(props.row)">
                    <li v-for="(message, index) in props.row.messages" :key="index">
                        {{ message }}
                    </li>
                </ul>
            </div>
        </template>
    </b-table>

    </section>
</template>

<script lang="ts">
/* eslint-disable class-methods-use-this */
import {
    Component, Vue, Prop, Watch
} from 'vue-property-decorator';
import {
    JobTargetError, isTargetError
} from '@/job/JobParameters';
import {
    MaybeJobTarget, JobTargetData, MonographMetadata, Person
} from './IngestMonographParameters';
import {
    getRecord, ZenonRecord, Author, AuthorTypes
} from '@/util/ZenonClient';
import {
    StagingDirectoryContents,
    getStagingFiles,
    containsNumberOfFiles,
    containsOnlyFilesWithExtensions
} from '@/staging/StagingClient';

@Component({
    filters: {
        truncate(value: string, length: number) {
            return value.length > length
                ? `${value.substr(0, length)}...`
                : value;
        }
    }
})
export default class MonographMetadataForm extends Vue {
    @Prop({ required: true }) private selectedPaths!: string[];

    targets: MaybeJobTarget[];

    constructor() {
        super();
        this.targets = [];
    }

    // Required to alert parent vue component of changes
    @Watch('targets')
    onPropertyChanged(value: MaybeJobTarget[], _oldValue: MaybeJobTarget[]) {
        this.$emit('update:targetsUpdated', value);
    }

    isTargetError = isTargetError;

    async mounted() {
        this.targets = await Promise.all(
            this.selectedPaths
                .map(this.processSelectedPath)
                .map(async(promise) => {
                    const target = await promise;
                    if (target instanceof JobTargetData) {
                        return this.loadZenonData(target);
                    }
                    return new JobTargetError(target.id, target.path, target.messages);
                })
        );
    }

    removeTarget(removedTarget: MaybeJobTarget) {
        this.targets = this.targets.filter(target => removedTarget.id !== target.id);
    }

    async processSelectedPath(path: string) : Promise<MaybeJobTarget> {
        const id = path.split('/').pop() || '';
        const zenonId = this.extractZenonId(path);
        let errors: string[] = [];
        if (zenonId === '') {
            errors.push(`Could not extract Zenon ID from ${path}.`);
        }

        const targetFolder = await getStagingFiles(path);
        if (Object.keys(targetFolder).length === 0) {
            errors.push(`Could not find file at ${path}.`);
        } else {
            errors = errors.concat(this.evaluateTargetFolder(targetFolder));
        }

        if (errors.length === 0) {
            return new JobTargetData(
                id, path, { zenon_id: zenonId } as MonographMetadata
            );
        }
        return new JobTargetError(id, path, errors);
    }

    evaluateTargetFolder(targetFolder : StagingDirectoryContents) {
        const errors: string[] = [];
        if (!containsNumberOfFiles(targetFolder, 1)) {
            errors.push(
                `Folder has more than one entry. Only one subfolder 'tif' is allowed.`
            );
        }

        if (!('tif' in targetFolder)) {
            errors.push(`Folder does not have a subfolder 'tif'.`);
        } else if (targetFolder.tif.contents !== undefined &&
                !containsOnlyFilesWithExtensions(targetFolder.tif.contents, ['.tif'])) {
            errors.push(`Subfolder 'tif' does not only contain files ending in '.tif'.`);
        }
        return errors;
    }

    extractZenonId(path: string): string {
        const result = path.match(/.*Book-ZID(\d+)/i);
        if (!result || result.length < 1) return '';
        return result[1];
    }

    filterDuplicateEntry<T>(value: T, index: number, array: T[]) {
        return array.indexOf(value) === index;
    }

    async loadZenonData(target: JobTargetData) : Promise<MaybeJobTarget> {
        try {
            const zenonRecord = await getRecord(target.metadata.zenon_id) as ZenonRecord;
            const errors : string[] = [];

            let summary = '';
            if (zenonRecord.summary.length > 0) {
                [summary] = zenonRecord.summary;
            }

            let subTitle = '';
            if (zenonRecord.subTitle) {
                subTitle = zenonRecord.subTitle.trim();
            }

            const filteredSubjects = zenonRecord.subjects
                .filter(this.filterDuplicateEntry);

            const authors = this.extractAuthors(zenonRecord);

            if (errors.length !== 0) {
                return new JobTargetError(target.id, target.path, errors);
            }
            const metadata = {
                zenon_id: target.metadata.zenon_id,
                press_code: 'dai',
                authors,
                title: zenonRecord.shortTitle,
                subtitle: subTitle,
                abstract: summary,
                date_published: zenonRecord.publicationDates[0],
                keywords: filteredSubjects
            } as MonographMetadata;

            return new JobTargetData(target.id, target.path, metadata);
        } catch (error) {
            return new JobTargetError(target.id, target.path, [error]);
        }
    }

    extractAuthors(record: ZenonRecord) : Person[] {
        return record.authors
            .map((author : Author) => {
                if (author.type === AuthorTypes.Corporate) {
                    return {
                        givenname: author.name,
                        lastname: ''
                    } as Person;
                }

                const authorSplit = author.name.split(',');
                if (authorSplit.length === 2) {
                    return {
                        givenname: authorSplit[1].replace(/[\\.]+$/, '').trim(),
                        lastname: authorSplit[0].trim()
                    } as Person;
                }
                return {
                    givenname: '',
                    lastname: author.name
                } as Person;
            });
    }
}

</script>

<style lang="scss" scoped>
.record-container {
    flex-wrap: wrap;
    padding-bottom: 2rem;
}
</style>
