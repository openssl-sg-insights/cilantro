import { JobParameters } from './JobParameters';
import { sendRequest } from '@/util/HTTPClient';
import { Job } from './Job';
import { backendUri } from '@/config';

export async function startJob(
    jobType: string,
    params: JobParameters
): Promise<boolean> {
    return sendRequest('post', `${backendUri}/job/${jobType}`, params, false);
}

export async function getJobList(): Promise<Job[]> {
    return sendRequest('get', `${backendUri}/job/jobs`, {}, false);
}

export async function getJobDetails(jobID: string): Promise<Job> {
    return sendRequest('get', `${backendUri}/job/${jobID}`, {}, false);
}
